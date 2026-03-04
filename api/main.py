"""
道义现实主义ABM系统的FastAPI后端

本模块是道义现实主义基于代理建模（ABM）系统的主要FastAPI应用程序。
它提供以下核心功能：
- 模拟控制：启动、暂停、恢复、停止模拟
- 代理管理：创建、查询、更新、删除代理
- 指标查询：获取当前和历史指标数据
- 检查点管理：保存和加载模拟状态
- WebSocket实时通信：推送模拟更新事件

核心概念：
- SimulationController：模拟控制器，管理整个模拟的生命周期
- WebSocketManager：WebSocket连接管理器，处理实时通信
- CORS配置：允许前端（React/Vue等）跨域访问API
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 全局模拟控制器实例
# 该控制器负责管理整个模拟的生命周期，包括代理、规则执行、事件生成等
simulation_controller: Optional["SimulationController"] = None
# 模拟任务的异步任务对象
sim_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用程序生命周期管理器

    该上下文管理器处理FastAPI应用的启动和关闭逻辑：
    - 启动时：初始化模拟控制器、设置路由引用
    - 关闭时：取消正在运行的模拟任务、清理资源



    Args:
        app: FastAPI应用实例
    """
    # 启动逻辑
    logger.info("正在启动道义现实主义ABM API...")
    initialize_simulation()  # 初始化模拟控制器
    yield
    # 关闭逻辑
    logger.info("正在关闭道义现实主义ABM API...")
    # 取消正在运行的模拟任务
    if sim_task and not sim_task.done():
        sim_task.cancel()
        try:
            await sim_task
        except asyncio.CancelledError:
            pass  # 正常的取消任务，忽略异常


def initialize_simulation():
    """
    初始化模拟控制器

    该函数负责创建模拟控制器实例，并将控制器的引用传递给各个路由模块。
    这样做是为了实现依赖注入，避免循环导入问题。

    主要步骤：
    1. 创建SimulationController实例
    2. 将控制器引用传递给各个路由模块
    3. 将WebSocket管理器引用传递给需要实时通信的路由
    """
    global simulation_controller
    # 延迟导入避免循环依赖
    from src.workflow.simulation_controller import SimulationController
    from src.agents.controller_agent import SimulationConfig

    try:
        # 创建模拟控制器实例，使用默认配置
        simulation_controller = SimulationController(config=SimulationConfig())
        logger.info("模拟控制器初始化成功")

        # 将控制器引用传递给各个路由模块
        # 这样路由就可以访问控制器，执行模拟操作
        from api.routes import simulation as sim_route, agents, metrics, checkpoints
        sim_route.set_controller(simulation_controller)
        sim_route.set_ws_manager(ws_manager)  # 设置WebSocket管理器引用
        agents.set_controller(simulation_controller)
        metrics.set_controller(simulation_controller)
        metrics.set_storage(simulation_controller._data_storage)  # 设置数据存储引用
        checkpoints.set_controller(simulation_controller)

    except Exception as e:
        logger.error(f"模拟控制器初始化失败: {e}")


# 创建FastAPI应用实例
app = FastAPI(
    title="道义现实主义ABM API",
    description="道义现实主义LLM驱动的基于代理建模系统API",
    version="1.0.0",
    lifespan=lifespan,  # 使用自定义生命周期管理器
)

# 配置跨域资源共享（CORS）
# 允许前端应用从不同的源访问API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite开发服务器默认端口
        "http://localhost:3000",  # Create React App默认端口
        "http://127.0.0.1:5173",  # Vite备用端口
        "http://127.0.0.1:3000",  # Create React App备用端口
    ],
    allow_credentials=True,  # 允许携带凭证（如cookies）
    allow_methods=["*"],    # 允许所有HTTP方法
    allow_headers=["*"],    # 允许所有请求头
)

# 创建WebSocket管理器实例
# 该管理器负责处理所有WebSocket连接和消息广播
from api.services.websocket_manager import WebSocketManager

ws_manager = WebSocketManager()

# 导入并注册路由模块
# 每个路由模块处理特定领域的API端点
from api.routes import simulation, agents, metrics, checkpoints

# 注册模拟控制路由（路径前缀: /api/v1/simulation）
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["simulation"])
# 注册代理管理路由（路径前缀: /api/v1/agents）
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
# 注册指标查询路由（路径前缀: /api/v1/metrics）
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
# 注册检查点管理路由（路径前缀: /api/v1/checkpoints）
app.include_router(checkpoints.router, prefix="/api/v1/checkpoints", tags=["checkpoints"])


@app.get("/")
async def root():
    """
    根路径端点

    返回API的基本信息，包括版本、状态和可用端点列表。
    该端点用于检查API是否正常运行，并获取可用服务的概览。

    Returns:
        包含API信息的字典，包括：
        - name: API名称
        - version: API版本
        - status: 当前运行状态
        - endpoints: 可用端点列表
    """
    return {
        "name": "道义现实主义ABM API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "simulation": "/api/v1/simulation",      # 模拟控制端点
            "agents": "/api/v1/agents",              # 代理管理端点
            "metrics": "/api/v1/metrics",            # 指标查询端点
            "checkpoints": "/api/v1/checkpoints",    # 检查点管理端点
            "websocket": "/ws/simulation/{simulation_id}",  # WebSocket端点
        },
    }


@app.get("/health")
async def health_check():
    """
    健康检查端点

    返回API的健康状态，用于监控和负载均衡器的心跳检测。
    该端点检查模拟控制器是否已正确初始化。

    Returns:
        包含健康状态的字典，包括：
        - status: API状态（healthy/ unhealthy）
        - simulation_initialized: 模拟控制器是否已初始化
    """
    return {
        "status": "healthy",
        "simulation_initialized": simulation_controller is not None,
    }


@app.websocket("/ws/simulation/{simulation_id}")
async def websocket_simulation(websocket: WebSocket, simulation_id: str):
    """
    WebSocket实时模拟更新端点

    该端点建立WebSocket连接，用于实时推送模拟更新事件。
    客户端可以连接到此端点接收以下类型的事件：
    - round_start: 回合开始事件
    - round_complete: 回合完成事件（包含回合指标）
    - simulation_complete: 模拟完成事件
    - error: 错误事件
    - status_update: 状态更新事件

    Args:
        websocket: FastAPI WebSocket连接对象
        simulation_id: 模拟会话标识符（用于区分不同的模拟实例）

    工作流程:
        1. 接受WebSocket连接
        2. 将连接添加到WebSocket管理器
        3. 持续监听来自客户端的消息
        4. 处理接收到的消息（如ping/pong心跳）
        5. 处理连接断开
    """
    # 接受WebSocket连接并将其添加到管理器
    await ws_manager.connect(websocket, simulation_id)
    try:
        while True:
            # 保持连接活跃并处理来自客户端的传入消息
            # 这允许客户端发送控制命令（如订阅特定事件）
            data = await websocket.receive_json()
            # 将消息传递给WebSocket管理器进行处理
            await ws_manager.handle_message(simulation_id, data)
    except WebSocketDisconnect:
        # 客户端主动断开连接
        ws_manager.disconnect(simulation_id)
        logger.info(f"WebSocket连接已断开: {simulation_id}")
    except Exception as e:
        # 处理其他异常（如网络错误）
        logger.error(f"WebSocket错误: {e}")
        ws_manager.disconnect(simulation_id)


# 导出模拟控制器供其他模块使用
__all__ = ["app", "simulation_controller", "ws_manager"]
