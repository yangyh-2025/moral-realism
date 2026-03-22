"""
WebSocket实时通信服务 - 实时事件推送

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    WebSocket连接管理器

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self):
        # 所有活跃连接: client_id -> WebSocket
        self._connections: Dict[str, WebSocket] = {}

        # 客户端到仿真的映射: client_id -> simulation_id
        self._client_simulation: Dict[str, str] = {}

        # 仿真到客户端的映射: simulation_id -> Set[client_id]
        self._simulation_clients: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """
        接受WebSocket连接

        Args:
            websocket: WebSocket连接
            client_id: 客户端ID
        """
        await websocket.accept()
        self._connections[client_id] = websocket
        logger.info(f"客户端 {client_id} 已连接")

    async def disconnect(self, client_id: str):
        """
        断开WebSocket连接

        Args:
            client_id: 客户端ID
        """
        if client_id in self._connections:
            del self._connections[client_id]

        if client_id in self._client_simulation:
            simulation_id = self._client_simulation[client_id]
            del self._client_simulation[client_id]

            if simulation_id in self._simulation_clients:
                self._simulation_clients[simulation_id].discard(client_id)
                if not self._simulation_clients[simulation_id]:
                    del self._simulation_clients[simulation_id]

        logger.info(f"客户端 {client_id} 已断开")

    async def send_personal_message(self, client_id: str, message: dict):
        """
        向指定客户端发送消息

        Args:
            client_id: 客户端ID
            message: 消息内容（字典格式）
        """
        if client_id not in self._connections:
            logger.warning(f"客户端 {client_id} 未连接")
            return

        try:
            websocket = self._connections[client_id]
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息到客户端 {client_id} 失败: {e}")
            await self.disconnect(client_id)

    async def broadcast(self, message: dict):
        """
        向所有连接的客户端广播消息

        Args:
            message: 消息内容（字典格式）
        """
        disconnected_clients = []

        for client_id, websocket in self._connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"广播消息到客户端 {client_id} 失败: {e}")
                disconnected_clients.append(client_id)

        # 清理断开的连接
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

    async def broadcast_to_simulation(self, simulation_id: str, message: dict):
        """
        向特定仿真的所有客户端广播消息

        Args:
            simulation_id: 仿真ID
            message: 消息内容（字典格式）
        """
        if simulation_id not in self._simulation_clients:
            return

        for client_id in self._simulation_clients[simulation_id]:
            await self.send_personal_message(client_id, message)

    async def push_order_update(self, simulation_id: str, order_info: dict):
        """
        推送秩序类型更新

        Args:
            simulation_id: 仿真ID
            order_info: 秩序评估信息
        """
        message = {
            "type": "order_update",
            "simulation_id": simulation_id,
            "data": order_info,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_simulation(simulation_id, message)

    def register_simulation_client(self, client_id: str, simulation_id: str):
        """
        注册客户端到仿真

        Args:
            client_id: 客户端ID
            simulation_id: 仿真ID
        """
        self._client_simulation[client_id] = simulation_id

        if simulation_id not in self._simulation_clients:
            self._simulation_clients[simulation_id] = set()

        self._simulation_clients[simulation_id].add(client_id)
        logger.info(f"客户端 {client_id} 已注册到仿真 {simulation_id}")

    def get_active_connections(self) -> int:
        """
        获取活跃连接数

        Returns:
            int: 活跃连接数
        """
        return len(self._connections)

    def get_simulation_clients(self, simulation_id: str) -> List[str]:
        """
        获取仿真的所有客户端

        Args:
            simulation_id: 仿真ID

        Returns:
            List[str]: 客户端ID列表
        """
        return list(self._simulation_clients.get(simulation_id, []))


class RealTimeEventPusher:
    """
    实时事件推送器

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def push_decision_event(self, simulation_id: str, decision: dict):
        """
        推送决策事件

        Args:
            simulation_id: 仿真ID
            decision: 决策数据
        """
        message = {
            "type": "decision",
            "simulation_id": simulation_id,
            "data": decision,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_simulation(simulation_id, message)

    async def push_action_event(self, simulation_id: str, action: dict):
        """
        推送动作事件

        Args:
            simulation_id: 仿真ID
            action: 动作数据
        """
        message = {
            "type": "action",
            "simulation_id": simulation_id,
            "data": action,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_simulation(simulation_id, message)

    async def push_metric_update(self, simulation: str, metrics: dict):
        """
        推送指标更新

        Args:
            simulation: 仿真ID
            metrics: 指标数据
        """
        message = {
            "type": "metrics",
            "simulation_id": simulation,
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_simulation(simulation, message)

    async def push_round_complete(self, simulation_id: str, round_info: dict):
        """
        推送轮次完成事件

        Args:
            simulation_id: 仿真ID
            round_info: 轮次信息
        """
        message = {
            "type": "round_complete",
            "simulation_id": simulation_id,
            "data": round_info,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_simulation(simulation_id, message)

    async def push_simulation_complete(self, simulation_id: str, result: dict):
        """
        推送仿真完成事件

        Args:
            simulation_id: 仿真ID
            result: 仿真结果
        """
        message = {
            "type": "simulation_complete",
            "simulation_id": simulation_id,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_simulation(simulation_id, message)

    async def push_error(self, simulation_id: str, error_info: dict):
        """
        推送错误事件

        Args:
            simulation_id: 仿真ID
            error_info: 错误信息
        """
        message = {
            "type": "error",
            "simulation_id": simulation_id,
            "data": error_info,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_simulation(simulation_id, message)

    async def push_agent_state_update(self, simulation_id: str, agent_id: str, state: dict):
        """
        推送智能体状态更新

        Args:
            simulation_id: 仿真ID
            agent_id: 智能体ID
            state: 状态数据
        """
        message = {
            "type": "agent_state_update",
            "simulation_id": simulation_id,
            "data": {
                "agent_id": agent_id,
                "state": state
            },
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_simulation(simulation_id, message)


# 全局连接管理器和事件推送器
_manager = ConnectionManager()
_event_pusher = RealTimeEventPusher(_manager)


def get_connection_manager() -> ConnectionManager:
    """获取全局连接管理器"""
    return _manager


def get_event_pusher() -> RealTimeEventPusher:
    """获取全局事件推送器"""
    return _event_pusher


@router.websocket("/simulation/{simulation_id}")
async def simulation_websocket(websocket: WebSocket, simulation_id: str):
    """
    仿真WebSocket端点

    Args:
        websocket: WebSocket连接
        simulation_id: 仿真ID
    """
    # 生成客户端ID（实际应用中可以从认证信息中获取）
    client_id = f"client_{simulation_id}_{id(websocket)}"

    try:
        # 连接建立
        await _manager.connect(websocket, client_id)
        _manager.register_simulation_client(client_id, simulation_id)

        # 发送连接确认消息
        await _manager.send_personal_message(client_id, {
            "type": "connected",
            "simulation_id": simulation_id,
            "message": "WebSocket连接已建立"
        })

        # 接收客户端消息
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # 处理客户端消息
                await _handle_client_message(client_id, simulation_id, message)

            except json.JSONDecodeError as e:
                logger.warning(f"无效的JSON消息: {e}")
                await _manager.send_personal_message(client_id, {
                    "type": "error",
                    "message": "无效的JSON消息"
                })
                continue  # 跳过后续处理

    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开: {client_id}")

    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        await _manager.send_personal_message(client_id, {
            "type": "error",
            "message": str(e)
        })

    finally:
        # 连接关闭
        await _manager.disconnect(client_id)


async def _handle_client_message(client_id: str, simulation_id: str, message: dict):
    """
    处理客户端消息

    Args:
        client_id: 客户端ID
        simulation_id:: 仿真ID
        message: 消息内容
    """
    message_type = message.get("type")

    if message_type == "ping":
        # 心跳响应
        await _manager.send_personal_message(client_id, {
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })

    elif message_type == "subscribe":
        # 订阅特定事件类型
        event_types = message.get("event_types", [])
        # 在实际实现中，这里会记录订阅的事件类型
        await _manager.send_personal_message(client_id, {
            "type": "subscribed",
            "event_types": event_types
        })

    elif message_type == "unsubscribe":
        # 取消订阅
        event_types = message.get("event_types", [])
        # 在实际实现中，这里会取消订阅
        await _manager.send_personal_message(client_id, {
            "type": "unsubscribed",
            "event_types": event_types
        })

    else:
        # 未知消息类型
        await _manager.send_personal_message(client_id, {
            "type": "error",
            "message": f"未知消息类型: {message_type}"
        })
