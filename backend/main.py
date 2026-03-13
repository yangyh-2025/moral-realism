"""
FastAPI 后端应用 - 核心API服务

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn

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
