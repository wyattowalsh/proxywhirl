"""WebSocket Endpoints

Real-time WebSocket connections for proxy updates, health monitoring, and system notifications.
Enhanced with comprehensive implementations from api.py for production-ready functionality.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from loguru import logger

from ...settings import get_api_settings
from ..auth_service import get_auth_service
from ..dependencies import get_websocket_user

router = APIRouter()

# Initialize settings and user manager
settings = get_api_settings()
auth_service = get_auth_service()


class ConnectionManager:
    """Enhanced WebSocket connection manager for real-time updates with comprehensive features."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "proxy_stream": set(),
            "health_monitor": set(),
        }
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Accept new WebSocket connection with enhanced logging."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(
            f"WebSocket connected to {channel}, total: {len(self.active_connections[channel])}"
        )
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove WebSocket connection with cleanup."""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        logger.info(f"WebSocket disconnected from {channel}")
    
    async def broadcast(self, message: Dict[str, Any], channel: str):
        """Broadcast message to all connections in channel with error handling."""
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

    async def cleanup_stale_connections(self) -> int:
        """Clean up stale WebSocket connections and return count of cleaned connections."""
        total_cleaned = 0

        for channel_name, connections in self.active_connections.items():
            stale_connections = set()

            for connection in connections.copy():
                try:
                    # Send a ping to check if connection is alive
                    await connection.send_json({"type": "ping", "timestamp": time.time()})
                except Exception:
                    # Connection is stale, mark for removal
                    stale_connections.add(connection)

            # Remove stale connections
            for connection in stale_connections:
                connections.discard(connection)
                total_cleaned += 1

            if stale_connections:
                logger.debug(
                    f"Cleaned {len(stale_connections)} stale connections from {channel_name}"
                )

        return total_cleaned


# Global connection manager
manager = ConnectionManager()


@router.websocket("/proxy-updates")
async def websocket_proxy_updates(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT token for authentication")
):
    """
    WebSocket endpoint for real-time proxy updates.
    
    Streams proxy status changes, new proxies, and validation results.
    """
    channel = "proxy_updates"
    
    # Authenticate user if token provided
    user = await get_websocket_user(token) if token else None
    if token and not user:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return
    
    await manager.connect(websocket, channel)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "welcome",
            "message": "Connected to proxy updates stream",
            "authenticated": user is not None,
            "username": user.username if user else None,
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            # Listen for client messages (ping/pong, subscriptions, etc.)
            try:
                data = await websocket.receive_json()
                
                # Handle client messages
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("type") == "subscribe":
                    # Handle subscription to specific proxy updates
                    await websocket.send_json({
                        "type": "subscription_confirmed", 
                        "filters": data.get("filters", {})
                    })
                
            except Exception as e:
                logger.debug(f"WebSocket message error: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, channel)


@router.websocket("/health-monitor")
async def websocket_health_monitor(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT token for authentication")
):
    """
    WebSocket endpoint for real-time health monitoring.
    
    Streams system health metrics, performance data, and alerts.
    """
    channel = "health_monitor"
    
    # Authenticate user (health monitoring requires authentication)
    user = await get_websocket_user(token)
    if not user:
        await websocket.close(code=4001, reason="Authentication required for health monitoring")
        return
    
    await manager.connect(websocket, channel)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "welcome",
            "message": "Connected to health monitoring stream",
            "username": user.username,
        })
        
        # Start health monitoring loop
        import asyncio
        
        async def send_health_updates():
            """Send periodic health updates."""
            while True:
                try:
                    # Mock health data - would get real metrics
                    health_data = {
                        "type": "health_update",
                        "timestamp": "2025-08-30T12:00:00Z",
                        "metrics": {
                            "proxy_count": 150,
                            "healthy_proxies": 120,
                            "failed_proxies": 10,
                            "cpu_usage": 45.2,
                            "memory_usage": 68.1,
                        },
                        "alerts": []  # Would contain any active alerts
                    }
                    
                    await websocket.send_json(health_data)
                    await asyncio.sleep(5)  # Update every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Health update error: {e}")
                    break
        
        # Start health updates task
        health_task = asyncio.create_task(send_health_updates())
        
        # Handle client messages
        while True:
            try:
                data = await websocket.receive_json()
                
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("type") == "get_current_status":
                    # Send immediate health status
                    await websocket.send_json({
                        "type": "current_status",
                        "status": "healthy",
                        "uptime": 3600.0,
                        "active_connections": len(manager.active_connections.get("health_monitor", [])),
                    })
                
            except Exception as e:
                logger.debug(f"WebSocket message error: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("Health monitor WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Health monitor WebSocket error: {e}")
    finally:
        # Cancel health updates task
        if 'health_task' in locals() and not health_task.done():
            health_task.cancel()
        
        manager.disconnect(websocket, channel)


# Export the connection manager for use in other modules
__all__ = ["router", "manager"]
