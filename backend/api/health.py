"""
健康检查端点

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, status
from datetime import datetime
import os
import sqlite3
import sys
from pathlib import Path

# 导入日志配置
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


# 缓存健康检查结果
_last_health_check = {
    "timestamp": None,
    "result": None
}


def get_database_status(db_path: str = "data/database.db") -> str:
    """检查数据库连接状态"""
    try:
        path = Path(db_path)
        if not path.exists():
            return "database_not_found"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return f"error: {str(e)}"


def get_llm_status() -> str:
    """检查LLM API可用性"""
    try:
        # 检查环境变量中是否有API Key配置
        import os
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("SILICONFLOW_API_KEY")
        if api_key:
            return "ok"
        else:
            return "no_api_key_configured"
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return f"error: {str(e)}"


def get_disk_status() -> str:
    """检查磁盘空间"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(os.getcwd())
        free_gb = free / (1024 ** 3)

        if free_gb < 1.0:
            return f"low_space: {free_gb:.2f}GB"
        return "ok"
    except Exception as e:
        logger.error(f"Disk health check failed: {e}")
        return f"error: {str(e)}"


def get_memory_status() -> str:
    """检查内存状态"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024 ** 3)

        if available_gb < 0.5:
            return f"low_memory: {available_gb:.2f}GB available"
        return f"ok: {available_gb:.2f}GB available"
    except ImportError:
        return "psutil_not_installed"
    except Exception as e:
        logger.error(f"Memory health check failed: {e}")
        return f"error: {str(e)}"


@router.get("/health", tags=["健康检查"])
async def health_check():
    """
    基础健康检查

    返回系统基本信息和运行状态
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.7.0",
        "service": "abm-simulation-api"
    }


@router.get("/health/dependencies", tags=["健康检查"])
async def dependency_check():
    """
    依赖项健康检查

    检查所有关键依赖的运行状态
    """
    db_path = os.getenv("DATABASE_PATH", "data/database.db")

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {
            "database": get_database_status(db_path),
            "llm_api": get_llm_status(),
            "disk": get_disk_status(),
            "memory": get_memory_status()
        }
    }


@router.get("/health/detailed", tags=["健康检查"])
async def detailed_health_check():
    """
    详细健康检查

    返回详细的系统信息，包括Python版本、依赖包版本等
    """
    import platform

    # 获取已安装包的版本信息
    packages = {}
    for module_name in ["fastapi", "uvicorn", "pydantic", "httpx"]:
        try:
            module = __import__(module_name)
            version = getattr(module, "__version__", "unknown")
            packages[module_name] = version
        except ImportError:
            packages[module_name] = "not_installed"

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "architecture": platform.machine()
        },
        "dependencies": {
            "database": get_database_status(os.getenv("DATABASE_PATH", "data/database.db")),
            "llm_api": get_llm_status(),
            "disk": get_disk_status(),
            "memory": get_memory_status()
        },
        "packages": packages,
        "environment": os.getenv("ENVIRONMENT", "dev")
    }


@router.get("/health/ready", tags=["健康检查"])
async def readiness_check():
    """
    就绪检查

    检查服务是否准备好接受请求
    """
    db_status = get_database_status(os.getenv("DATABASE_PATH", "data/database.db"))

    is_ready = db_status == "ok"

    response_data = {
        "ready": is_ready,
        "timestamp": datetime.now().isoformat()
    }

    if not is_ready:
        response_data["message"] = "Service not ready"
        response_data["checks"] = {
            "database": db_status
        }
        return response_data, status.HTTP_503_SERVICE_UNAVAILABLE

    return response_data


@router.get("/health/live", tags=["健康检查"])
async def liveness_check():
    """
    存活检查

    检查服务是否仍在运行（轻量级检查）
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }
