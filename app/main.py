"""
FastAPI 应用程序入口点
国际秩序ABM仿真系统的主入口文件，负责初始化应用程序、配置中间件、路由和启动服务器。
"""

from contextlib import asynccontextmanager
from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from loguru import logger
from dotenv import load_dotenv

from .api.router import api_router
from .config.database import db_config, init_database, init_default_data
from .config.logging_config import setup_logging

# 加载环境变量
load_dotenv()

# 配置日志系统
setup_logging(log_level="INFO")

# 获取项目根目录路径
BASE_DIR = Path(__file__).resolve().parent.parent
# 前端构建目录路径
FRONTEND_DIR = BASE_DIR / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 应用生命周期管理器

    在应用启动时初始化数据库和默认数据，在应用关闭时清理数据库连接。

    Args:
        app: FastAPI 应用实例
    """
    # 应用启动阶段
    logger.info("正在初始化数据库...")
    await init_database()
    logger.info("正在初始化默认数据...")
    await init_default_data()
    logger.info("应用启动完成")

    # 应用运行期间
    yield

    # 应用关闭阶段
    logger.info("应用正在关闭...")
    await db_config.close()

# 创建 FastAPI 应用实例
app = FastAPI(
    title="International Order ABM Simulation System",
    description="基于大语言模型的国际秩序ABM仿真系统 - 克莱因国力方程修订版V1.3",
    version="1.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 配置跨域资源共享 (CORS) 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源，生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router)


@app.get("/")
async def root():
    """
    根路径端点 - 提供前端页面

    如果前端构建文件存在，则返回 index.html，否则返回系统信息。
    """
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "system": "International Order ABM Simulation System",
        "version": "1.3.0",
        "description": "基于大语言模型的国际秩序ABM仿真系统",
        "status": "running",
        "docs": "/docs",
        "api_prefix": "/api/v1"
    }


@app.get("/health")
async def health_check():
    """
    健康检查端点

    用于监控系统是否正常运行。
    """
    return {
        "status": "healthy",
        "system": "International Order ABM"
    }


# 挂载前端静态资源（如果存在）
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")


# 独立运行模式
if __name__ == "__main__":
    import uvicorn
    logger.info("以独立模式启动服务器")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
