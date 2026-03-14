"""
FastAPI 后端应用 - 核心API服务

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn
import os

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
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip响应压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 导入并注册API路由
from backend.api.simulation import router as simulation_router
from backend.api.agents import router as agents_router
from backend.api.events import router as events_router
from backend.api.data import router as data_router
from backend.api.export import router as export_router
from backend.api.ws import router as ws_router

app.include_router(simulation_router, prefix="/api/simulation", tags=["仿真管理"])
app.include_router(agents_router, prefix="/api/agents", tags=["智能体管理"])
app.include_router(events_router, prefix="/api/events", tags=["事件管理"])
app.include_router(data_router, prefix="/api/data", tags=["数据查询"])
app.include_router(export_router, prefix="/api/export", tags=["结果导出"])
app.include_router(ws_router, prefix="/api/ws", tags=["WebSocket"])

if __name__ == "__main__":
    # 开发模式启动
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
