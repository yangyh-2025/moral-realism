"""
FastAPI 后端应用 - 核心API服务

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import List
import uvicorn
import traceback
import os

# 导入自定义错误类
from interfaces.errors.errors import CustomError

# 导入日志配置
from infrastructure.logging.logging_config import configure_logging, get_logger

# 配置日志
configure_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/app.log"),
    json_logs=os.getenv("ENVIRONMENT", "dev") == "production"
)

# 获取日志记录器
logger = get_logger(__name__)

# 数据库连接池配置
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# 数据库路径配置
DATABASE_DIR = "data"
DATABASE_FILE = os.path.join(DATABASE_DIR, "database.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# 创建连接池
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # 连接池大小
    max_overflow=10,         # 最大溢出连接数
    pool_timeout=30,         # 获取连接超时时间
    pool_recycle=3600,       # 连接回收时间(秒)
    pool_pre_ping=True,      # 连接前ping检查
    echo=False              # 是否打印SQL语句
)

# 创建FastAPI应用实例
app = FastAPI(
    title="道义现实主义社会模拟仿真系统 API",
    description="基于LLM的社会模拟仿真系统后端API",
    version="1.7.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS 配置
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# GZip响应压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 导入并启用速率限制中间件
from backend.middleware.ratelimit import RateLimiter

# 创建速率限制中间件实例
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


class RateLimitMiddleware:
    """速率限制中间件类"""

    async def __call__(self, request, call_next):
        """处理请求前检查速率限制"""
        client_id = request.client.host if request.client else "unknown"

        if not rate_limiter.is_allowed(client_id):
            from fastapi import status
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": {"message": "Rate limit exceeded", "code": "RATE_LIMIT_EXCEEDED", "status_code": 429}}
            )

        response = await call_next(request)
        return response


# 添加速率限制中间件
app.add_middleware(RateLimitMiddleware)

# 全局异常处理器
@app.exception_handler(CustomError)
async def custom_error_handler(request: Request, exc: CustomError):
    """处理自定义错误"""
    logger.warning(
        f"Custom error: {exc.code} - {exc.message}",
        error_code=exc.code,
        status_code=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exception_type=type(exc).__name__,
        traceback=traceback.format_exc()
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "code": "INTERNAL_ERROR",
                "status_code": 500,
                "details": {
                    "traceback": traceback.format_exc() if app.debug else None
                }
            }
        }
    )

# 导入并注册API路由
from backend.api.simulation import router as simulation_router
from backend.api.agents import router as agents_router
from backend.api.events import router as events_router
from backend.api.data import router as data_router
from backend.api.export import router as export_router
from backend.api.ws import router as ws_router
from backend.api.health import router as health_router

app.include_router(simulation_router, prefix="/api/simulation", tags=["仿真管理"])
app.include_router(agents_router, prefix="/api/agents", tags=["智能体管理"])
app.include_router(events_router, prefix="/api/events", tags=["事件管理"])
app.include_router(data_router, prefix="/api/data", tags=["数据查询"])
app.include_router(export_router, prefix="/api/export", tags=["结果导出"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])
app.include_router(health_router, tags=["健康检查"])


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("ABM Simulation API starting up", version="1.7.0")

    # 初始化性能监控
    from infrastructure.performance import performance_monitor
    logger.info("Performance monitoring initialized")

    # 初始化服务（依赖注入）
    from backend.services.export_service import ExportService
    from backend.services.simulation_manager import SimulationLifecycle

    app.state.export_service = ExportService()
    app.state.simulation_manager = SimulationLifecycle()

    logger.info("Services initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("ABM Simulation API shutting down")

    # 输出性能指标
    from infrastructure.performance import performance_monitor
    metrics = performance_monitor.get_metrics()
    logger.info("Performance metrics summary", metrics=metrics)


if __name__ == "__main__":
    # 开发模式启动
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
