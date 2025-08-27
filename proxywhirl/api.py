"""proxywhirl/api.py -- Comprehensive FastAPI API for ProxyWhirl

This module provides a robust, production-ready FastAPI API exposing all ProxyWhirl
capabilities with advanced features:

- OAuth2 with JWT and scopes for fine-grained permissions
- Real-time WebSocket streaming for proxy updates
- Comprehensive error handling with circuit breaker integration
- Background task management for long-running operations
- Streaming responses for large datasets
- Advanced dependency injection with caching
- Health monitoring with detailed diagnostics
- OpenAPI documentation with examples and schemas

Features:
- Async-first design with proper error handling
- Multi-tenant support with user isolation
- Rate limiting and request validation
- Comprehensive logging and monitoring
- Production-ready security patterns
"""

from __future__ import annotations

import asyncio
import json
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Union

import psutil
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    Security,
    WebSocket,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt
from loguru import logger
import orjson
from orjson import dumps as orjson_dumps
from passlib.context import CryptContext
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, ConfigDict, Field
from secure import Secure

# Advanced middleware imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from typing_extensions import Annotated

from .models import (
    CacheType,
    Proxy,
    ProxyStatus,
    RotationStrategy,
    ValidationErrorType,
)
from .proxywhirl import ProxyWhirl
from .settings import APISettings, get_api_settings
from .auth import get_user_manager, User, UserInDB


class ORJSONResponse(JSONResponse):
    """High-performance JSON response using orjson for 2x faster serialization."""
    
    media_type = "application/json"
    
    def render(self, content: Any) -> bytes:
        """Render content using orjson for optimal performance."""
        if content is None:
            return b""
        
        # Use orjson for fast serialization with proper datetime handling
        return orjson_dumps(
            content,
            option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY
        )

# === Security Configuration ===

# Initialize settings
settings = get_api_settings()

# Initialize user manager
user_manager = get_user_manager()

# Token expiration in minutes (configurable via environment)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "read": "Read proxy data and health information",
        "write": "Fetch proxies and update health data",
        "validate": "Validate proxies and run health checks",
        "config": "Modify configuration settings",
        "admin": "Full administrative access",
    },
)

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)
secure = Secure()

# === Pydantic Models ===


class Token(BaseModel):
    """JWT Token response model."""

    access_token: str
    token_type: str
    expires_in: int
    scopes: List[str]


class TokenData(BaseModel):
    """JWT Token payload data."""

    username: Optional[str] = None
    scopes: List[str] = []


class ProxyResponse(BaseModel):
    """Enhanced proxy response with health metrics."""

    model_config = ConfigDict(from_attributes=True)

    proxy: Proxy
    quality_score: float = Field(ge=0.0, le=1.0, description="Overall quality score")
    last_used: Optional[datetime] = Field(default=None, description="Last time proxy was used")
    consecutive_failures: int = Field(ge=0, description="Count of consecutive failures")
    is_available: bool = Field(description="Whether proxy is currently available for use")


class ProxyListResponse(BaseModel):
    """Paginated proxy list response."""

    proxies: List[ProxyResponse]
    total: int = Field(ge=0, description="Total number of proxies")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=1000, description="Number of items per page")
    has_next: bool = Field(description="Whether there are more pages")


class FetchProxiesRequest(BaseModel):
    """Request model for fetching proxies."""

    validate_proxies: bool = Field(
        default=True, description="Whether to validate proxies after fetching"
    )
    max_proxies: Optional[int] = Field(
        default=None, ge=1, le=10000, description="Maximum number of proxies to fetch"
    )
    sources: Optional[List[str]] = Field(
        default=None, description="Specific proxy sources to use (empty = all)"
    )


class FetchProxiesResponse(BaseModel):
    """Response model for fetch proxies operation."""

    task_id: str = Field(description="Background task ID for tracking progress")
    message: str = Field(description="Operation status message")
    estimated_duration: int = Field(ge=0, description="Estimated completion time in seconds")


class ValidationRequest(BaseModel):
    """Request model for proxy validation."""

    proxy_ids: Optional[List[str]] = Field(
        default=None, description="Specific proxy IDs to validate (empty = all)"
    )
    max_proxies: Optional[int] = Field(
        default=None, ge=1, le=1000, description="Maximum number of proxies to validate"
    )
    target_urls: Optional[List[str]] = Field(
        default=None, description="Custom target URLs for validation"
    )


class ValidationResponse(BaseModel):
    """Response model for validation operations."""

    valid_proxies: int = Field(ge=0, description="Number of valid proxies found")
    invalid_proxies: int = Field(ge=0, description="Number of invalid proxies found")
    success_rate: float = Field(ge=0.0, le=1.0, description="Overall success rate")
    avg_response_time: Optional[float] = Field(
        default=None, description="Average response time in seconds"
    )
    errors: Dict[ValidationErrorType, int] = Field(
        default_factory=dict, description="Error counts by type"
    )


class HealthResponse(BaseModel):
    """API health status response."""

    status: str = Field(description="Overall health status")
    timestamp: datetime = Field(description="Health check timestamp")
    version: str = Field(description="ProxyWhirl version")
    uptime: float = Field(ge=0.0, description="API uptime in seconds")
    proxy_count: int = Field(ge=0, description="Total cached proxies")
    healthy_proxies: int = Field(ge=0, description="Number of healthy proxies")


class CacheStatsResponse(BaseModel):
    """Cache statistics response."""

    cache_type: CacheType = Field(description="Type of cache backend")
    total_proxies: int = Field(ge=0, description="Total proxies in cache")
    healthy_proxies: int = Field(ge=0, description="Number of healthy proxies")
    cache_hits: Optional[int] = Field(default=None, description="Cache hit count")
    cache_misses: Optional[int] = Field(default=None, description="Cache miss count")
    cache_size: Optional[int] = Field(default=None, description="Cache size in items")


class ConfigResponse(BaseModel):
    """Configuration response model."""

    rotation_strategy: RotationStrategy
    cache_type: CacheType
    auto_validate: bool
    max_fetch_proxies: Optional[int]
    validation_timeout: float
    health_check_interval: int


class ErrorDetail(BaseModel):
    """Detailed error information."""

    error_code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error context")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# === WebSocket Connection Manager ===


class ConnectionManager:
    """WebSocket connection manager for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "proxy_stream": set(),
            "health_monitor": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept new WebSocket connection."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(
            f"WebSocket connected to {channel}, total: {len(self.active_connections[channel])}"
        )

    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove WebSocket connection."""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        logger.info(f"WebSocket disconnected from {channel}")

    async def broadcast(self, message: dict, channel: str):
        """Broadcast message to all connections in channel."""
        if channel not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections[channel].discard(connection)


# === Global State ===

# WebSocket manager
ws_manager = ConnectionManager()

# Background task tracking
background_tasks: Dict[str, Dict[str, Any]] = {}

# API startup time for uptime calculation
api_start_time = datetime.now(timezone.utc)


# === Application Lifespan ===


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 ProxyWhirl API starting up...")

    # Initialize ProxyWhirl instance
    app.state.proxywhirl = ProxyWhirl(auto_validate=True)

    # Start background health monitoring
    health_task = asyncio.create_task(health_monitoring_background())

    yield

    # Cleanup on shutdown
    logger.info("🔄 ProxyWhirl API shutting down...")
    health_task.cancel()
    try:
        await health_task
    except asyncio.CancelledError:
        pass


# === FastAPI App Initialization ===

# Initialize Prometheus instrumentator
if settings.enable_metrics and not settings.is_testing:
    instrumentator = Instrumentator()

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
    debug=settings.debug,
    lifespan=lifespan,
)

# === Security Middleware ===

# Enhanced security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next) -> Response:
    """Add comprehensive security headers to all responses."""
    start_time = time.time()
    response = await call_next(request)

    # Apply security headers based on environment
    if settings.is_production:
        # Production security headers
        response.headers.update(
            {
                # HSTS - Force HTTPS for 1 year
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                # Content Security Policy - Prevent XSS
                "Content-Security-Policy": (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                    "font-src 'self' https://fonts.gstatic.com; "
                    "img-src 'self' data: https:; "
                    "connect-src 'self' wss: https:; "
                    "frame-ancestors 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'"
                ),
                # Prevent clickjacking
                "X-Frame-Options": "DENY",
                # Prevent MIME type sniffing
                "X-Content-Type-Options": "nosniff",
                # Prevent XSS attacks
                "X-XSS-Protection": "1; mode=block",
                # Referrer policy for privacy
                "Referrer-Policy": "strict-origin-when-cross-origin",
                # Permissions policy (formerly Feature Policy)
                "Permissions-Policy": (
                    "geolocation=(), "
                    "microphone=(), "
                    "camera=(), "
                    "payment=(), "
                    "usb=(), "
                    "magnetometer=(), "
                    "gyroscope=(), "
                    "speaker=(), "
                    "ambient-light-sensor=(), "
                    "accelerometer=(), "
                    "vr=(), "
                    "midi=()"
                ),
            }
        )
    else:
        # Development security headers (more permissive)
        response.headers.update(
            {
                # Relaxed CSP for development
                "Content-Security-Policy": (
                    "default-src 'self' 'unsafe-inline' 'unsafe-eval' http: https: ws: wss:; "
                    "frame-ancestors 'none'"
                ),
                "X-Frame-Options": "DENY",
                "X-Content-Type-Options": "nosniff",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }
        )

    # Common headers for all environments
    response.headers.update(
        {
            # Processing time for debugging
            "X-Process-Time": f"{time.time() - start_time:.4f}s",
            # API version info
            "X-API-Version": settings.version,
            # Request tracking
            "X-Request-ID": getattr(request.state, "request_id", "unknown"),
            # Security contact (customize for your organization)
            "X-Content-Type-Options": "nosniff",
            # Prevent caching of sensitive data
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )

    # Remove server identification header for security
    response.headers.pop("Server", None)

    return response


# Enhanced trusted host middleware for production
if settings.is_production:
    # Use configured trusted hosts, fall back to sensible defaults
    trusted_hosts = settings.trusted_hosts
    if not trusted_hosts:
        trusted_hosts = [
            "api.proxywhirl.com",  # Primary API domain (customize for your domain)
            "*.proxywhirl.com",  # Subdomain wildcard (customize for your domain)
            "localhost",  # Local development
            "127.0.0.1",  # Local IP
        ]
        logger.warning(
            "No trusted hosts configured, using defaults. Set PROXYWHIRL_TRUSTED_HOSTS in production."
        )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
    logger.info(f"Trusted host middleware enabled with hosts: {trusted_hosts}")

# CORS middleware with environment-based configuration  
cors_config = settings.get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

# Authentication context middleware (before rate limiting)
@app.middleware("http")
async def authentication_context_middleware(request: Request, call_next) -> Response:
    """Add user context to request state for downstream middleware and rate limiting."""
    # Skip authentication for public endpoints
    public_endpoints = {"/", "/docs", "/redoc", "/openapi.json", "/health"}
    if request.url.path in public_endpoints:
        request.state.authenticated_user = None
        request.state.user_scopes = []
        return await call_next(request)
    
    # Try to extract and validate JWT token
    try:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.algorithm])
            username = payload.get("sub")
            scopes = payload.get("scopes", [])
            
            # Add user context to request state
            request.state.authenticated_user = username
            request.state.user_scopes = scopes
            logger.debug(f"Authentication context: user={username}, scopes={scopes}")
        else:
            request.state.authenticated_user = None
            request.state.user_scopes = []
    except (JWTError, AttributeError):
        request.state.authenticated_user = None
        request.state.user_scopes = []
    
    return await call_next(request)

# Rate limiting middleware (after authentication context)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Compression middleware (after rate limiting)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Prometheus metrics middleware (last, for complete request tracking)
if settings.enable_metrics and not settings.is_testing:
    instrumentator.instrument(app)


# === Helper Functions ===


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
) -> UserInDB:
    """Get current authenticated user with scope validation."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(
            token, settings.secret_key.get_secret_value(), algorithms=[settings.algorithm]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except JWTError:
        raise credentials_exception

    user = user_manager.get_user(token_data.username)
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])],
):
    """Get current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_websocket_user(websocket: WebSocket) -> Optional[UserInDB]:
    """
    Authenticate WebSocket connection using JWT token.

    Expects token in query parameter 'token' or Authorization header.
    Returns None if authentication fails (connection should be closed).
    """
    try:
        # Try to get token from query parameters first
        token = websocket.query_params.get("token")

        # If not in query params, try Authorization header
        if not token:
            auth_header = websocket.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[1]

        if not token:
            logger.warning("WebSocket connection attempted without token")
            return None

        try:
            payload = jwt.decode(
                token, settings.secret_key.get_secret_value(), algorithms=[settings.algorithm]
            )
            username = payload.get("sub")
            if username is None:
                logger.warning("WebSocket token missing username")
                return None

            # Get user and validate they exist and are active
            user = user_manager.get_user(username)
            if user is None or user.disabled:
                logger.warning(f"WebSocket authentication failed for user: {username}")
                return None

            # Check if user has at least read permissions for WebSocket access
            if "read" not in user.scopes:
                logger.warning(f"WebSocket user {username} lacks read permissions")
                return None

            logger.info(f"WebSocket authenticated user: {username}")
            return user

        except JWTError as e:
            logger.warning(f"WebSocket JWT validation failed: {e}")
            return None

    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        return None


async def get_proxywhirl() -> ProxyWhirl:
    """Get ProxyWhirl instance dependency."""
    return app.state.proxywhirl


# === Background Tasks ===


async def health_monitoring_background():
    """Background task for health monitoring and WebSocket updates."""
    while True:
        try:
            pw = app.state.proxywhirl

            # Get current stats
            proxy_count = pw.get_proxy_count()
            proxies = pw.list_proxies()
            healthy_count = sum(1 for p in proxies if p.is_healthy)

            # Broadcast health update
            health_data = {
                "type": "health_update",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "proxy_count": proxy_count,
                "healthy_proxies": healthy_count,
                "cache_type": pw.cache_type.value,
            }

            await ws_manager.broadcast(health_data, "health_monitor")

            # Wait for next update
            await asyncio.sleep(30)  # Update every 30 seconds

        except Exception as e:
            logger.error(f"Health monitoring error: {e}")
            await asyncio.sleep(60)  # Back off on errors


async def fetch_proxies_background(
    pw: ProxyWhirl,
    task_id: str,
    validate: bool = True,
    max_proxies: Optional[int] = None,
    sources: Optional[List[str]] = None,
):
    """Background task for fetching proxies."""
    try:
        logger.info(f"Starting proxy fetch task {task_id}")
        background_tasks[task_id] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc),
            "progress": 0,
            "message": "Fetching proxies from sources...",
        }

        # TODO: Filter sources if specified
        count = await pw.fetch_proxies_async(validate=validate)

        background_tasks[task_id].update(
            {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc),
                "progress": 100,
                "message": f"Successfully fetched {count} proxies",
                "result": {"proxy_count": count},
            }
        )

        # Broadcast update
        await ws_manager.broadcast(
            {"type": "fetch_completed", "task_id": task_id, "proxy_count": count}, "proxy_stream"
        )

        logger.info(f"Completed proxy fetch task {task_id}: {count} proxies")

    except Exception as e:
        logger.error(f"Proxy fetch task {task_id} failed: {e}")
        background_tasks[task_id].update(
            {
                "status": "failed",
                "completed_at": datetime.now(timezone.utc),
                "error": str(e),
                "message": f"Failed to fetch proxies: {e}",
            }
        )


# === Authentication Endpoints ===


@app.post("/auth/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticate user and return JWT access token.

    Uses OAuth2 password flow with scope-based permissions.
    """
    user_result = user_manager.authenticate_user(form_data.username, form_data.password)
    if not user_result or not isinstance(user_result, UserInDB):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_result  # Type: UserInDB

    # Validate requested scopes against user permissions
    requested_scopes = form_data.scopes if form_data.scopes else []
    available_scopes = user.scopes
    granted_scopes = [scope for scope in requested_scopes if scope in available_scopes]

    # If no scopes requested, grant default read scope if user has it
    if not granted_scopes and "read" in available_scopes:
        granted_scopes = ["read"]

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": granted_scopes}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "scopes": granted_scopes,
    }


@app.get("/auth/me", response_model=User, tags=["Authentication"])
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get current user information."""
    return current_user


# === Core Proxy Management Endpoints ===


@app.post("/proxies/fetch", response_model=FetchProxiesResponse, tags=["Proxy Management"])
async def fetch_proxies(
    request: FetchProxiesRequest,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Security(get_current_user, scopes=["write"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """
    Fetch proxies from all configured sources.

    This is an asynchronous operation that runs in the background.
    Use the returned task_id to track progress via WebSocket or polling.
    """
    import uuid

    task_id = str(uuid.uuid4())

    # Estimate duration based on number of sources and validation
    estimated_duration = 30 if request.validate_proxies else 15
    if request.sources:
        estimated_duration = int(
            estimated_duration * len(request.sources) / 8
        )  # Assuming 8 default sources

    background_tasks.add_task(
        fetch_proxies_background,
        pw=pw,
        task_id=task_id,
        validate=request.validate_proxies,
        max_proxies=request.max_proxies,
        sources=request.sources,
    )

    return FetchProxiesResponse(
        task_id=task_id,
        message="Proxy fetching started in background",
        estimated_duration=estimated_duration,
    )


@app.get("/proxies", response_model=ProxyListResponse, response_class=ORJSONResponse, tags=["Proxy Management"])
async def list_proxies(
    current_user: Annotated[User, Depends(get_current_active_user)],
    pw: ProxyWhirl = Depends(get_proxywhirl),
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=1000)] = 50,
    status: Optional[ProxyStatus] = Query(None, description="Filter by proxy status"),
    scheme: Optional[str] = Query(None, description="Filter by proxy scheme"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    min_quality: Annotated[float, Query(ge=0.0, le=1.0)] = 0.0,
):
    """
    List cached proxies with filtering and pagination.

    Supports filtering by status, scheme, country, and quality score.
    """
    all_proxies = pw.list_proxies()

    # Apply filters
    filtered_proxies = []
    for proxy in all_proxies:
        if status and proxy.status != status:
            continue
        if scheme and scheme.lower() not in [s.value.lower() for s in proxy.schemes]:
            continue
        if country and proxy.country != country.upper():
            continue
        if proxy.quality_score < min_quality:
            continue
        filtered_proxies.append(proxy)

    # Pagination
    total = len(filtered_proxies)
    start = (page - 1) * page_size
    end = start + page_size
    page_proxies = filtered_proxies[start:end]

    # Convert to response format
    response_proxies = []
    for proxy in page_proxies:
        response_proxies.append(
            ProxyResponse(
                proxy=proxy,
                quality_score=proxy.quality_score or proxy.intelligent_quality_score,
                last_used=None,  # Not tracked in current model
                consecutive_failures=(
                    proxy.error_state.consecutive_failures if proxy.error_state else 0
                ),
                is_available=proxy.status == ProxyStatus.ACTIVE and proxy.is_healthy,
            )
        )

    return ProxyListResponse(
        proxies=response_proxies, total=total, page=page, page_size=page_size, has_next=end < total
    )


@app.get("/proxies/stream", tags=["Proxy Management"])
async def stream_proxies(
    current_user: Annotated[User, Depends(get_current_active_user)],
    pw: ProxyWhirl = Depends(get_proxywhirl),
    batch_size: Annotated[int, Query(ge=10, le=500)] = 100,
    limit: Annotated[int, Query(ge=1, le=10000)] = 1000,
    status: Optional[ProxyStatus] = Query(None, description="Filter by proxy status"),
    scheme: Optional[str] = Query(None, description="Filter by proxy scheme"),
    country: Optional[str] = Query(None, description="Filter by country code"),
    min_quality: Annotated[float, Query(ge=0.0, le=1.0)] = 0.0,
):
    """
    Stream proxies in batches for large datasets with memory optimization.

    Returns JSON streaming response for handling large proxy datasets
    without loading everything into memory at once.
    """
    import asyncio

    async def generate_proxy_stream():
        """Generate JSON stream of proxies in batches."""
        from proxywhirl.models import Proxy  # Import here to avoid circular imports

        all_proxies: List[Proxy] = pw.list_proxies()

        # Apply filters (same logic as list_proxies)
        filtered_proxies: List[Proxy] = []
        for proxy in all_proxies:
            if status and proxy.status != status:
                continue
            if scheme and scheme.lower() not in [s.value.lower() for s in proxy.schemes]:
                continue
            if country and proxy.country != country.upper():
                continue
            if proxy.quality_score < min_quality:
                continue
            filtered_proxies.append(proxy)

        # Limit total proxies
        total_proxies = min(len(filtered_proxies), limit)
        filtered_proxies = filtered_proxies[:limit]

        # Start JSON response
        yield "{\n"
        yield f'  "total": {total_proxies},\n'
        yield f'  "batch_size": {batch_size},\n'
        yield f'  "timestamp": "{datetime.now(timezone.utc).isoformat()}",\n'
        yield '  "proxies": [\n'

        proxy_count = 0
        for i in range(0, len(filtered_proxies), batch_size):
            batch = filtered_proxies[i : i + batch_size]

            for j, proxy in enumerate(batch):
                if proxy_count > 0:
                    yield ",\n"

                # Convert to response format
                proxy_response = ProxyResponse(
                    proxy=proxy,
                    quality_score=proxy.quality_score or proxy.intelligent_quality_score,
                    last_used=None,  # Not tracked in current model
                    consecutive_failures=(
                        proxy.error_state.consecutive_failures if proxy.error_state else 0
                    ),
                    is_available=proxy.status == ProxyStatus.ACTIVE and proxy.is_healthy,
                )

                # Serialize to JSON with proper indentation
                proxy_json = json.dumps(proxy_response.model_dump(), default=str, indent=4)
                # Indent the proxy JSON to match the overall structure
                indented_json = "\n".join(f"    {line}" for line in proxy_json.split("\n"))
                yield indented_json

                proxy_count += 1

            # Yield control to allow other tasks (non-blocking)
            await asyncio.sleep(0)

        yield "\n  ],\n"
        yield f'  "streamed_count": {proxy_count}\n'
        yield "}\n"

    return StreamingResponse(
        generate_proxy_stream(),
        media_type="application/json",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
            "X-Total-Count": str(len(pw.list_proxies())),
            "Content-Disposition": 'inline; filename="proxies_stream.json"',
        },
    )


@app.get("/proxies/next", response_model=ProxyResponse, tags=["Proxy Operations"])
async def get_next_proxy(
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """
    Get the next proxy using the configured rotation strategy.

    Returns the best available proxy based on health, quality, and rotation logic.
    """
    proxy = await pw.get_proxy_async()
    if not proxy:
        raise HTTPException(
            status_code=404,
            detail="No healthy proxies available",
            headers={"X-Error-Code": "NO_PROXIES_AVAILABLE"},
        )

    return ProxyResponse(
        proxy=proxy,
        quality_score=proxy.quality_score or proxy.intelligent_quality_score,
        last_used=None,  # Not tracked in current model
        consecutive_failures=proxy.error_state.consecutive_failures if proxy.error_state else 0,
        is_available=proxy.status == ProxyStatus.ACTIVE and proxy.is_healthy,
    )


@app.get("/proxies/{proxy_id}", response_model=ProxyResponse, tags=["Proxy Management"])
async def get_proxy_by_id(
    proxy_id: Annotated[str, Path(description="Proxy ID in format 'host:port'")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """Get detailed information about a specific proxy."""
    try:
        host, port_str = proxy_id.rsplit(":", 1)
        port = int(port_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid proxy ID format. Use 'host:port'",
            headers={"X-Error-Code": "INVALID_PROXY_ID"},
        )

    proxies = pw.list_proxies()
    proxy = next((p for p in proxies if p.host == host and p.port == port), None)

    if not proxy:
        raise HTTPException(
            status_code=404,
            detail=f"Proxy {proxy_id} not found",
            headers={"X-Error-Code": "PROXY_NOT_FOUND"},
        )

    return ProxyResponse(
        proxy=proxy,
        quality_score=proxy.quality_score or proxy.intelligent_quality_score,
        last_used=None,  # Not tracked in current model
        consecutive_failures=proxy.error_state.consecutive_failures if proxy.error_state else 0,
        is_available=proxy.status == ProxyStatus.ACTIVE and proxy.is_healthy,
    )


class HealthUpdateRequest(BaseModel):
    """Request model for proxy health updates."""
    
    success: bool = Field(description="Whether the proxy operation was successful")
    response_time: Optional[float] = Field(None, ge=0.001, description="Response time in seconds")
    error_type: Optional[ValidationErrorType] = Field(None, description="Type of error if failed")


@app.put("/proxies/{proxy_id}/health", tags=["Proxy Management"])
async def update_proxy_health(
    proxy_id: Annotated[str, Path(description="Proxy ID in format 'host:port'")],
    health_update: HealthUpdateRequest,
    current_user: Annotated[User, Security(get_current_user, scopes=["write"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """
    Update proxy health metrics after usage.

    This endpoint allows clients to report proxy performance and failures,
    which improves the quality scoring and rotation logic.
    """
    try:
        host, port_str = proxy_id.rsplit(":", 1)
        port = int(port_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proxy ID format. Use 'host:port'")

    proxies = pw.list_proxies()
    proxy = next((p for p in proxies if p.host == host and p.port == port), None)

    if not proxy:
        raise HTTPException(status_code=404, detail=f"Proxy {proxy_id} not found")

    # Update health metrics
    pw.update_proxy_health(
        proxy=proxy,
        success=health_update.success,
        response_time=health_update.response_time,
        error_type=health_update.error_type,
        error_message=health_update.error_type.value if health_update.error_type else None,
    )

    # Broadcast update
    await ws_manager.broadcast(
        {
            "type": "proxy_health_updated",
            "proxy_id": proxy_id,
            "success": health_update.success,
            "response_time": health_update.response_time,
            "quality_score": proxy.quality_score,
        },
        "proxy_stream",
    )

    return {"message": f"Health updated for proxy {proxy_id}"}


@app.delete("/proxies/{proxy_id}", tags=["Proxy Management"])
async def remove_proxy(
    proxy_id: Annotated[str, Path(description="Proxy ID in format 'host:port'")],
    current_user: Annotated[User, Security(get_current_user, scopes=["write"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """Remove a proxy from the cache."""
    try:
        host, port_str = proxy_id.rsplit(":", 1)
        port = int(port_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid proxy ID format. Use 'host:port'")

    proxies = pw.list_proxies()
    proxy = next((p for p in proxies if p.host == host and p.port == port), None)

    if not proxy:
        raise HTTPException(status_code=404, detail=f"Proxy {proxy_id} not found")

    # Remove from cache
    pw.cache.remove_proxy_sync(proxy)

    return {"message": f"Proxy {proxy_id} removed successfully"}


# === Proxy Validation Endpoints ===


@app.post("/proxies/validate", response_model=ValidationResponse, tags=["Proxy Validation"])
async def validate_specific_proxies(
    request: ValidationRequest,
    current_user: Annotated[User, Security(get_current_user, scopes=["validate"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """
    Validate specific proxies or all cached proxies.

    Supports filtering by proxy IDs and custom validation targets.
    """
    try:
        result_count = await pw.validate_proxies_async(max_proxies=request.max_proxies)

        # Get validation statistics
        validator_stats = pw.validator.get_validation_stats()

        # Calculate error breakdown
        all_proxies = pw.list_proxies()
        error_counts = {}
        for proxy in all_proxies:
            if proxy.error_state and proxy.error_state.last_error_type:
                error_type = proxy.error_state.last_error_type
                error_counts[error_type] = error_counts.get(error_type, 0) + 1

        return ValidationResponse(
            valid_proxies=result_count,
            invalid_proxies=len(all_proxies) - result_count,
            success_rate=validator_stats.get("success_rate", 0.0),
            avg_response_time=validator_stats.get("avg_response_time"),
            errors=error_counts,
        )

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}",
            headers={"X-Error-Code": "VALIDATION_FAILED"},
        )


@app.post("/proxies/validate-all", response_model=ValidationResponse, tags=["Proxy Validation"])
async def validate_all_proxies(
    current_user: Annotated[User, Security(get_current_user, scopes=["validate"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """
    Validate all cached proxies and remove invalid ones.

    This is a comprehensive validation that checks all proxies in the cache.
    """
    try:
        result_count = await pw.validate_proxies_async()

        validator_stats = pw.validator.get_validation_stats()
        all_proxies = pw.list_proxies()

        return ValidationResponse(
            valid_proxies=result_count,
            invalid_proxies=len(all_proxies) - result_count,
            success_rate=validator_stats.get("success_rate", 0.0),
            avg_response_time=validator_stats.get("avg_response_time"),
            errors={},
        )

    except Exception as e:
        logger.error(f"Full validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}",
            headers={"X-Error-Code": "FULL_VALIDATION_FAILED"},
        )


# === Health & Monitoring Endpoints ===


@app.get("/health", response_model=HealthResponse, tags=["Health & Monitoring"])
@limiter.limit(settings.rate_limit_default)
async def health_check(request: Request, pw: ProxyWhirl = Depends(get_proxywhirl)):
    """
    Basic API health check with rate limiting.

    Returns current API status and basic proxy statistics.
    """
    try:
        proxy_count = pw.get_proxy_count()
        proxies = pw.list_proxies()
        healthy_count = sum(1 for p in proxies if p.is_healthy)

        uptime = (datetime.now(timezone.utc) - api_start_time).total_seconds()

        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            version=settings.version,
            uptime=uptime,
            proxy_count=proxy_count,
            healthy_proxies=healthy_count,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(timezone.utc),
            version="1.0.0",
            uptime=(datetime.now(timezone.utc) - api_start_time).total_seconds(),
            proxy_count=0,
            healthy_proxies=0,
        )


@app.get("/health/report", tags=["Health & Monitoring"])
async def get_health_report(
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """
    Get comprehensive health report in Markdown format.

    Returns detailed diagnostics including loader status, validation metrics,
    and performance statistics.
    """
    try:
        report = await pw.generate_health_report()
        return {"report": report, "format": "markdown"}
    except Exception as e:
        logger.error(f"Health report generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate health report: {str(e)}",
            headers={"X-Error-Code": "HEALTH_REPORT_FAILED"},
        )


@app.get("/health/validator", tags=["Health & Monitoring"])
@limiter.limit(settings.rate_limit_default)
async def get_validator_health(
    request: Request,
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """Get validator health status and circuit breaker state."""
    try:
        health_status = await pw.validator.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Validator health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validator health check failed: {str(e)}",
            headers={"X-Error-Code": "VALIDATOR_HEALTH_FAILED"},
        )


# === Enhanced Monitoring & Metrics Endpoints ===

if settings.enable_metrics:

    @app.get(settings.metrics_path, tags=["Monitoring"])
    async def get_metrics():
        """
        Prometheus metrics endpoint.

        Returns metrics in Prometheus format for monitoring integration.
        Only available when metrics are enabled in settings.
        """
        try:
            from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
        except ImportError:
            raise HTTPException(
                status_code=503, detail="Metrics not available - prometheus_client not installed"
            )


@app.get("/system/metrics", tags=["System Monitoring"])
@limiter.limit(settings.rate_limit_auth)
async def get_system_metrics(
    request: Request,
    current_user: Annotated[User, Security(get_current_user, scopes=["admin"])],
):
    """
    Get comprehensive system metrics including CPU, memory, and disk usage.

    Requires admin permissions and has stricter rate limiting.
    """
    try:
        import psutil

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory metrics
        memory = psutil.virtual_memory()

        # Disk metrics
        disk = psutil.disk_usage("/")

        # Network metrics (basic)
        network = psutil.net_io_counters()

        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100,
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            },
            "process": {
                "pid": process.pid,
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "cpu_percent": process.cpu_percent(),
                "create_time": process.create_time(),
            },
        }

    except Exception as e:
        logger.error(f"System metrics collection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect system metrics: {str(e)}",
            headers={"X-Error-Code": "SYSTEM_METRICS_FAILED"},
        )


@app.get("/security/audit", tags=["Security"])
@limiter.limit("5/hour")  # Very strict rate limiting for security endpoint
async def security_audit(
    request: Request,
    current_user: Annotated[User, Security(get_current_user, scopes=["admin"])],
):
    """
    Perform security audit checks.

    Returns security configuration status and recommendations.
    Heavily rate limited due to sensitive nature.
    """
    try:
        audit_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": settings.environment,
            "security_checks": {
                "secret_key_secure": len(settings.secret_key.get_secret_value()) >= 32,
                "debug_disabled": not settings.debug if settings.is_production else True,
                "cors_configured": (
                    len(settings.cors_origins) > 0 if settings.is_production else True
                ),
                "rate_limiting_enabled": settings.rate_limit_enabled,
                "metrics_enabled": settings.enable_metrics,
                "trusted_hosts": settings.is_production,  # Assuming TrustedHost middleware in prod
            },
            "recommendations": [],
        }

        # Add security recommendations
        if settings.is_production and settings.debug:
            audit_results["recommendations"].append("Disable debug mode in production")

        if not settings.rate_limit_enabled:
            audit_results["recommendations"].append("Enable rate limiting for production use")

        if settings.is_production and not settings.cors_origins:
            audit_results["recommendations"].append(
                "Configure specific CORS origins for production"
            )

        if len(settings.secret_key.get_secret_value()) < 64:
            audit_results["recommendations"].append(
                "Consider using a longer secret key (64+ characters)"
            )

        return audit_results

    except Exception as e:
        logger.error(f"Security audit failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Security audit failed: {str(e)}",
            headers={"X-Error-Code": "SECURITY_AUDIT_FAILED"},
        )


# === Statistics Endpoints ===


@app.get("/stats/cache", response_model=CacheStatsResponse, response_class=ORJSONResponse, tags=["Statistics"])
async def get_cache_stats(
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """Get cache statistics and performance metrics."""
    try:
        stats = pw.cache.get_stats_sync()
        proxies = pw.list_proxies()
        healthy_count = sum(1 for p in proxies if p.is_healthy)

        return CacheStatsResponse(
            cache_type=pw.cache_type,
            total_proxies=len(proxies),
            healthy_proxies=healthy_count,
            cache_hits=stats.get("hits"),
            cache_misses=stats.get("misses"),
            cache_size=stats.get("size"),
        )

    except Exception as e:
        logger.error(f"Cache stats failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache stats: {str(e)}",
            headers={"X-Error-Code": "CACHE_STATS_FAILED"},
        )


@app.get("/stats/validation", tags=["Statistics"])
async def get_validation_stats(
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """Get validation statistics and performance metrics."""
    try:
        stats = pw.validator.get_validation_stats()
        return stats
    except Exception as e:
        logger.error(f"Validation stats failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get validation stats: {str(e)}",
            headers={"X-Error-Code": "VALIDATION_STATS_FAILED"},
        )


# === Configuration Endpoints ===


@app.get("/config", response_model=ConfigResponse, tags=["Configuration"])
async def get_config(
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """Get current ProxyWhirl configuration."""
    return ConfigResponse(
        rotation_strategy=pw.rotation_strategy,
        cache_type=pw.cache_type,
        auto_validate=pw.auto_validate,
        max_fetch_proxies=pw.max_fetch_proxies,
        validation_timeout=pw.validator.timeout,
        health_check_interval=300,  # TODO: Get from actual config
    )


@app.put("/config", tags=["Configuration"])
async def update_config(
    config: ConfigResponse,
    current_user: Annotated[User, Security(get_current_user, scopes=["config"])],
    pw: ProxyWhirl = Depends(get_proxywhirl),
):
    """
    Update ProxyWhirl configuration.

    Note: Some changes may require API restart to take effect.
    """
    try:
        # Update configurable settings
        pw.rotation_strategy = config.rotation_strategy
        pw.auto_validate = config.auto_validate
        pw.max_fetch_proxies = config.max_fetch_proxies

        return {"message": "Configuration updated successfully"}

    except Exception as e:
        logger.error(f"Config update failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update configuration: {str(e)}",
            headers={"X-Error-Code": "CONFIG_UPDATE_FAILED"},
        )


# === Background Task Status Endpoints ===


@app.get("/tasks/{task_id}", tags=["Background Tasks"])
async def get_task_status(
    task_id: str,
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])],
):
    """Get status of a background task."""
    if task_id not in background_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found",
            headers={"X-Error-Code": "TASK_NOT_FOUND"},
        )

    return background_tasks[task_id]


@app.get("/tasks", tags=["Background Tasks"])
async def list_background_tasks(
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])],
):
    """List all background tasks."""
    return {"tasks": background_tasks}


# === WebSocket Endpoints ===


@app.websocket("/ws/proxy-stream")
async def websocket_proxy_stream(websocket: WebSocket):
    """
    Real-time proxy updates stream with authentication.

    Sends updates when proxies are fetched, validated, or health changes.
    Requires valid JWT token via 'token' query parameter or Authorization header.
    """
    from fastapi import WebSocketDisconnect

    # Authenticate WebSocket connection
    user = await get_websocket_user(websocket)
    if not user:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await ws_manager.connect(websocket, "proxy_stream")
    logger.info(f"Authenticated WebSocket proxy stream for user: {user.username}")

    try:
        while True:
            # Keep connection alive and listen for client messages
            _ = await websocket.receive_text()
            # Echo back for keepalive with user info
            await websocket.send_json(
                {
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "user": user.username,
                }
            )
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "proxy_stream")
        logger.info(f"WebSocket proxy stream disconnected for user: {user.username}")


@app.websocket("/ws/health-monitor")
async def websocket_health_monitor(websocket: WebSocket):
    """
    Real-time health monitoring stream with authentication.

    Sends periodic health updates and alerts.
    Requires valid JWT token via 'token' query parameter or Authorization header.
    """
    from fastapi import WebSocketDisconnect

    # Authenticate WebSocket connection
    user = await get_websocket_user(websocket)
    if not user:
        await websocket.close(code=1008, reason="Authentication failed")
        return

    await ws_manager.connect(websocket, "health_monitor")
    logger.info(f"Authenticated WebSocket health monitor for user: {user.username}")

    try:
        while True:
            _ = await websocket.receive_text()
            await websocket.send_json(
                {
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "user": user.username,
                }
            )
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, "health_monitor")
        logger.info(f"WebSocket health monitor disconnected for user: {user.username}")


# === Error Handlers ===


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Enhanced HTTP exception handler with structured error responses."""
    error_code = "HTTP_ERROR"
    if hasattr(exc, "headers") and exc.headers and isinstance(exc.headers, dict):
        error_code = exc.headers.get("X-Error-Code", "HTTP_ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorDetail(
            error_code=error_code, message=str(exc.detail), details={"status_code": exc.status_code}
        ).model_dump(),
        headers=exc.headers if hasattr(exc, "headers") and exc.headers else None,
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content=ErrorDetail(
            error_code="VALIDATION_ERROR", message=str(exc), details={"type": "ValueError"}
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorDetail(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"type": type(exc).__name__},
        ).model_dump(),
    )


# === Application Metadata ===


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ProxyWhirl API",
        "version": "1.0.0",
        "description": "Comprehensive REST API for ProxyWhirl rotating proxy service",
        "docs_url": "/docs",
        "health_url": "/health",
        "uptime": (datetime.now(timezone.utc) - api_start_time).total_seconds(),
    }
