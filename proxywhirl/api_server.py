#!/usr/bin/env python3
"""
ProxyWhirl API Server

Production-ready startup script for the ProxyWhirl FastAPI server.
Supports both development and production modes with comprehensive configuration.

Usage:
    python -m proxywhirl.api_server                    # Development mode
    python -m proxywhirl.api_server --production       # Production mode
    python -m proxywhirl.api_server --host 0.0.0.0     # Custom host
    python -m proxywhirl.api_server --port 8080        # Custom port

Environment Variables:
    PROXYWHIRL_SECRET_KEY     - JWT secret key (required for production)
    PROXYWHIRL_HOST           - Server host (default: 127.0.0.1)
    PROXYWHIRL_PORT           - Server port (default: 8000)
    PROXYWHIRL_RELOAD         - Enable auto-reload (default: False)
    PROXYWHIRL_WORKERS        - Number of worker processes (production only)
"""

import os
import sys
from typing import Optional

import typer
import uvicorn
from loguru import logger

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = typer.Typer(help="ProxyWhirl FastAPI Server")


def configure_logging(level: str = "INFO"):
    """Configure logging for the API server."""
    # Remove default logger
    logger.remove()

    # Add console logging with colors
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        diagnose=True,
        backtrace=True,
    )

    # Add file logging for production
    if level == "INFO":
        logger.add(
            "logs/proxywhirl-api.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="gz",
        )


@app.command()
def serve(
    host: str = typer.Option(
        os.getenv("PROXYWHIRL_HOST", "127.0.0.1"), "--host", "-h", help="Host to bind the server to"
    ),
    port: int = typer.Option(
        int(os.getenv("PROXYWHIRL_PORT", "8000")), "--port", "-p", help="Port to bind the server to"
    ),
    production: bool = typer.Option(
        False, "--production", "--prod", help="Run in production mode with multiple workers"
    ),
    reload: bool = typer.Option(
        os.getenv("PROXYWHIRL_RELOAD", "false").lower() == "true",
        "--reload",
        "--dev",
        help="Enable auto-reload for development",
    ),
    workers: Optional[int] = typer.Option(
        int(os.getenv("PROXYWHIRL_WORKERS", "4")) if os.getenv("PROXYWHIRL_WORKERS") else None,
        "--workers",
        "-w",
        help="Number of worker processes (production mode only)",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Logging level (DEBUG, INFO, WARNING, ERROR)",
        case_sensitive=False,
    ),
    access_log: bool = typer.Option(
        True, "--access-log/--no-access-log", help="Enable/disable access logging"
    ),
):
    """
    Start the ProxyWhirl FastAPI server.

    The server provides a comprehensive REST API for managing rotating proxies
    with OAuth2 authentication, real-time WebSocket updates, and background tasks.
    """
    # Validate environment for production
    if production:
        secret_key = os.getenv("PROXYWHIRL_SECRET_KEY")
        if not secret_key or secret_key == "your-secret-key-change-in-production":
            logger.error(
                "🚨 PROXYWHIRL_SECRET_KEY environment variable must be set for production!"
            )
            logger.error("   Generate a secure key with: openssl rand -hex 32")
            sys.exit(1)

        if reload:
            logger.warning("🔄 Auto-reload disabled in production mode")
            reload = False

        if not workers:
            workers = 4

    # Configure logging
    configure_logging(log_level.upper())

    # Import the FastAPI app
    try:
        from proxywhirl.api import app as fastapi_app

        logger.success("✅ ProxyWhirl API loaded successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import ProxyWhirl API: {e}")
        sys.exit(1)

    # Server configuration
    server_config = {
        "app": "proxywhirl.api:app",
        "host": host,
        "port": port,
        "reload": reload and not production,
        "access_log": access_log,
        "log_level": log_level.lower(),
        "server_header": False,  # Hide server header for security
        "date_header": False,  # Hide date header for security
    }

    # Production-specific configuration
    if production:
        server_config.update(
            {
                "workers": workers,
                "worker_class": "uvicorn.workers.UvicornWorker",
                "preload_app": True,
                "max_requests": 1000,
                "max_requests_jitter": 100,
                "timeout_keep_alive": 2,
            }
        )
        logger.info(f"🚀 Starting ProxyWhirl API in production mode with {workers} workers")
    else:
        logger.info("🔧 Starting ProxyWhirl API in development mode")

    # Display startup information
    logger.info(f"📡 Server: http://{host}:{port}")
    logger.info(f"📚 Documentation: http://{host}:{port}/docs")
    logger.info(f"🔍 Health Check: http://{host}:{port}/health")
    logger.info(f"🔐 Authentication: http://{host}:{port}/auth/token")

    # Start the server
    try:
        if production:
            # Use Gunicorn for production with multiple workers
            import gunicorn.app.wsgiapp as wsgi

            # Configure Gunicorn
            gunicorn_config = [
                "proxywhirl.api:app",
                "--bind",
                f"{host}:{port}",
                "--workers",
                str(workers),
                "--worker-class",
                "uvicorn.workers.UvicornWorker",
                "--worker-connections",
                "1000",
                "--max-requests",
                "1000",
                "--max-requests-jitter",
                "100",
                "--timeout",
                "30",
                "--keep-alive",
                "2",
                "--log-level",
                log_level.lower(),
                "--access-logfile",
                "-" if access_log else "/dev/null",
                "--error-logfile",
                "-",
                "--preload",
            ]

            # Set Gunicorn configuration via sys.argv
            sys.argv = ["gunicorn"] + gunicorn_config
            wsgi.run()
        else:
            # Use Uvicorn for development
            uvicorn.run(**server_config)

    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 Server failed to start: {e}")
        sys.exit(1)


@app.command()
def health():
    """Check if the ProxyWhirl API is running and healthy."""
    import httpx

    host = os.getenv("PROXYWHIRL_HOST", "127.0.0.1")
    port = int(os.getenv("PROXYWHIRL_PORT", "8000"))

    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            logger.success(f"✅ ProxyWhirl API is healthy")
            logger.info(f"   Status: {data.get('status')}")
            logger.info(f"   Uptime: {data.get('uptime', 0):.1f}s")
            logger.info(f"   Proxies: {data.get('proxy_count', 0)}")
            logger.info(f"   Healthy Proxies: {data.get('healthy_proxies', 0)}")
        else:
            logger.error(f"❌ API returned status {response.status_code}")
            sys.exit(1)
    except httpx.ConnectError:
        logger.error(f"❌ Cannot connect to API at http://{host}:{port}")
        logger.info("   Make sure the server is running with: python -m proxywhirl.api_server")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        sys.exit(1)


@app.command()
def openapi():
    """Generate and display the OpenAPI schema."""
    try:
        import json

        from proxywhirl.api import app as fastapi_app

        schema = fastapi_app.openapi()
        print(json.dumps(schema, indent=2))
    except Exception as e:
        logger.error(f"Failed to generate OpenAPI schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Run the Typer app
    app()
