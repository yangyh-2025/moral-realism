"""
WebSocket连接管理器模块

本模块提供WebSocketManager类，用于：
- 管理活跃的WebSocket连接
- 向连接的客户端广播模拟更新事件
- 处理客户端消息

支持的事件类型：
- round_start: 回合开始
- round_complete: 回合完成
- simulation_complete: 模拟完成
- checkpoint_saved: 检查点已保存
- metrics_update: 指标更新
- status_update: 状态更新
- error: 错误事件
- log: 日志消息
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket

from api.models.schemas import (
    WSConnected,
    WSLogMessage,
    WSErrorMessage,
    WSMessageType,
)


logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manager for WebSocket connections.

    Handles:
    - Connection lifecycle (connect/disconnect)
    - Message broadcasting
    - Per-simulation connection management
    """

    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.simulation_subscribers: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, simulation_id: str) -> None:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection.
            simulation_id: Simulation session ID.
        """
        await websocket.accept()

        # Store connection
        connection_id = f"{simulation_id}_{id(websocket)}"
        self.active_connections[connection_id] = websocket

        # Add to simulation subscribers
        if simulation_id not in self.simulation_subscribers:
            self.simulation_subscribers[simulation_id] = set()
        self.simulation_subscribers[simulation_id].add(connection_id)

        # Send connected message
        connected_msg = WSConnected(
            simulation_id=simulation_id,
            timestamp=datetime.now().isoformat()
        ).dict()
        await websocket.send_json(connected_msg)

        logger.info(f"WebSocket connected: {connection_id}")

    def disconnect(self, connection_id: str) -> None:
        """
        Remove a WebSocket connection.

        Args:
            connection_id: Connection ID to remove.
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket disconnected: {connection_id}")

        # Remove from simulation subscribers
        for sim_id, subs in self.simulation_subscribers.items():
            if connection_id in subs:
                subs.remove(connection_id)
                if not subs:
                    del self.simulation_subscribers[sim_id]

    async def broadcast_to_simulation(
        self,
        simulation_id: str,
        message: Dict[str, Any],
    ) -> None:
        """
        Broadcast a message to all subscribers of a simulation.

        Args:
            simulation_id: Simulation session ID.
            message: Message to broadcast.
        """
        if simulation_id not in self.simulation_subscribers:
            return

        # Send to all subscribers
        dead_connections = []
        for connection_id in self.simulation_subscribers[simulation_id]:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to {connection_id}: {e}")
                    dead_connections.append(connection_id)

        # Clean up dead connections
        for conn_id in dead_connections:
            self.disconnect(conn_id)

    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all active connections.

        Args:
            message: Message to broadcast.
        """
        dead_connections = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")
                dead_connections.append(connection_id)

        # Clean up dead connections
        for conn_id in dead_connections:
            self.disconnect(conn_id)

    async def send_log(
        self,
        simulation_id: str,
        level: str,
        message: str,
    ) -> None:
        """
        Send a log message to simulation subscribers.

        Args:
            simulation_id: Simulation session ID.
            level: Log level (INFO, WARNING, ERROR).
            message: Log message content.
        """
        log_msg = WSLogMessage(
            level=level,
            message=message,
            timestamp=datetime.now().isoformat(),
        ).dict()
        await self.broadcast_to_simulation(simulation_id, log_msg)

    async def send_error(
        self,
        simulation_id: str,
        error: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send an error message to simulation subscribers.

        Args:
            simulation_id: Simulation session ID.
            error: Error message.
            details: Additional error details.
        """
        error_msg = WSErrorMessage(
            error=error,
            details=details,
            timestamp=datetime.now().isoformat(),
        ).dict()
        await self.broadcast_to_simulation(simulation_id, error_msg)

    async def send_round_start(
        self,
        simulation_id: str,
        round_number: int,
    ) -> None:
        """
        Send round start notification.

        Args:
            simulation_id: Simulation session ID.
            round_number: Current round number.
        """
        message = {
            "type": WSMessageType.ROUND_START,
            "simulation_id": simulation_id,
            "round": round_number,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_simulation(simulation_id, message)

    async def send_round_complete(
        self,
        simulation_id: str,
        round_number: int,
        metrics: Dict[str, Any],
    ) -> None:
        """
        Send round completion notification with metrics.

        Args:
            simulation_id: Simulation session ID.
            round_number: Completed round number.
            metrics: Round metrics data.
        """
        message = {
            "type": WSMessageType.ROUND_COMPLETE,
            "simulation_id": simulation_id,
            "round": round_number,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_simulation(simulation_id, message)

    async def send_simulation_complete(
        self,
        simulation_id: str,
        summary: Dict[str, Any],
    ) -> None:
        """
        Send simulation completion notification.

        Args:
            simulation_id: Simulation session ID.
            summary: Simulation summary data.
        """
        message = {
            "type": WSMessageType.SIMULATION_COMPLETE,
            "simulation_id": simulation_id,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_simulation(simulation_id, message)

    async def send_checkpoint_saved(
        self,
        simulation_id: str,
        checkpoint_id: str,
    ) -> None:
        """
        Send checkpoint saved notification.

        Args:
            simulation_id: Simulation session ID.
            checkpoint_id: Checkpoint ID.
        """
        message = {
            "type": WSMessageType.CHECKPOINT_SAVED,
            "simulation_id": simulation_id,
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_simulation(simulation_id, message)

    async def send_metrics_update(
        self,
        simulation_id: str,
        metrics: Dict[str, Any],
    ) -> None:
        """
        Send metrics update.

        Args:
            simulation_id: Simulation session ID.
            metrics: Current metrics data.
        """
        message = {
            "type": WSMessageType.METRICS_UPDATE,
            "simulation_id": simulation_id,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_simulation(simulation_id, message)

    async def send_status_update(
        self,
        simulation_id: str,
        status: str,
        state: Dict[str, Any],
    ) -> None:
        """
        Send status update.

        Args:
            simulation_id: Simulation session ID.
            status: Current status.
            state: Current state data.
        """
        message = {
            "type": WSMessageType.STATUS_UPDATE,
            "simulation_id": simulation_id,
            "status": status,
            "state": state,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_simulation(simulation_id, message)

    async def handle_message(
        self,
        simulation_id: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Handle incoming WebSocket message.

        Args:
            simulation_id: Simulation session ID.
            data: Message data.
        """
        message_type = data.get("type", "")

        # Handle different message types
        if message_type == "ping":
            # Respond to ping with pong
            await self.broadcast_to_simulation(
                simulation_id,
                {"type": "pong", "timestamp": datetime.now().isoformat()},
            )
        elif message_type == "subscribe_logs":
            # Log subscription (could filter by agent_id, level, etc.)
            pass
        elif message_type == "get_status":
            # Send current status
            pass
        else:
            logger.warning(f"Unknown WebSocket message type: {message_type}")

    def get_connection_count(self, simulation_id: str) -> int:
        """
        Get number of active connections for a simulation.

        Args:
            simulation_id: Simulation session ID.

        Returns:
            Number of active connections.
        """
        if simulation_id not in self.simulation_subscribers:
            return 0
        return len(self.simulation_subscribers[simulation_id])

    def has_subscribers(self, simulation_id: str) -> bool:
        """
        Check if simulation has any active subscribers.

        Args:
            simulation_id: Simulation session ID.

        Returns:
            True if has active subscribers.
        """
        return self.get_connection_count(simulation_id) > 0
