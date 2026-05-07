"""
系统配置管理服务（数据库支持版）

负责全局系统配置的读取和更新。
核心改造：
- 配置持久化到 SystemConfig 表
- 启动时从数据库加载，覆盖环境变量默认值
- 更新时同步刷新 LLMService 的客户端配置（这样前端配置真正生效）
"""

from typing import Dict, Any, Optional
import os

from loguru import logger
from sqlalchemy import select

from app.config.database import db_config
from app.models import SystemConfig


# 系统配置默认值（首次启动或DB无值时使用）
DEFAULT_CONFIG: Dict[str, Any] = {
    "llm_model_name": os.getenv("LLM_MODEL", "gpt-4"),
    "llm_api_key": os.getenv("OPENAI_API_KEY", ""),
    "llm_api_base": os.getenv("OPENAI_API_BASE", ""),
    "llm_timeout": int(os.getenv("LLM_TIMEOUT", "60")),
    "llm_max_retries": int(os.getenv("LLM_MAX_RETRIES", "3")),
    "simulation_concurrency": int(os.getenv("SIMULATION_CONCURRENCY", "5")),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "default_scene_id": 1,
}

# 数值型配置项的解析规则
_INT_KEYS = {"llm_timeout", "llm_max_retries", "simulation_concurrency", "default_scene_id"}


def _coerce_value(key: str, raw: Any) -> Any:
    """将字符串配置值转换为正确的Python类型"""
    if raw is None:
        return DEFAULT_CONFIG.get(key)
    if key in _INT_KEYS:
        try:
            return int(raw)
        except (ValueError, TypeError):
            return DEFAULT_CONFIG.get(key)
    return str(raw)


class SystemConfigService:
    """
    系统配置管理服务

    持久化策略：
    - 配置存储在 system_config 表（key/value 行格式）
    - 内存中维护一份缓存以加速读取
    - 启动时从DB懒加载（首次访问时）
    """

    def __init__(self):
        # 内存缓存。首次访问时从DB加载。
        self._config: Dict[str, Any] = dict(DEFAULT_CONFIG)
        self._loaded_from_db = False

    async def _ensure_loaded(self) -> None:
        """首次访问前从数据库加载配置（懒加载）"""
        if self._loaded_from_db:
            return

        try:
            async for session in db_config.get_session():
                result = await session.execute(select(SystemConfig))
                rows = result.scalars().all()
                for row in rows:
                    if row.config_key in self._config or row.config_key in DEFAULT_CONFIG:
                        self._config[row.config_key] = _coerce_value(
                            row.config_key, row.config_value
                        )
            self._loaded_from_db = True
            logger.info(f"SystemConfig 已从数据库加载，共 {len(self._config)} 项")
        except Exception as e:
            logger.warning(f"从数据库加载SystemConfig失败，使用环境变量默认值: {e}")
            self._loaded_from_db = True  # 避免反复重试

    async def _persist_to_db(self, updates: Dict[str, Any]) -> None:
        """将更新写入 system_config 表（upsert 模式）"""
        try:
            async for session in db_config.get_session():
                for key, value in updates.items():
                    result = await session.execute(
                        select(SystemConfig).where(SystemConfig.config_key == key)
                    )
                    existing = result.scalar_one_or_none()
                    str_value = "" if value is None else str(value)
                    if existing is not None:
                        existing.config_value = str_value
                    else:
                        session.add(
                            SystemConfig(
                                config_key=key,
                                config_value=str_value,
                                config_desc=f"系统配置项: {key}",
                            )
                        )
                await session.commit()
        except Exception as e:
            logger.error(f"持久化SystemConfig到数据库失败: {e}", exc_info=True)

    def _apply_to_llm_service(self) -> None:
        """将当前配置同步到全局 LLMService 单例"""
        try:
            # 延迟导入避免循环依赖
            from app.services.llm_service import LLMConfig, get_llm_service

            new_cfg = LLMConfig(
                provider="openai",
                model_name=self._config.get("llm_model_name", "gpt-4"),
                api_key=self._config.get("llm_api_key", ""),
                api_base=self._config.get("llm_api_base", "") or "",
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                timeout=int(self._config.get("llm_timeout", 60)),
                max_retries=int(self._config.get("llm_max_retries", 3)),
                retry_delay=float(os.getenv("LLM_RETRY_DELAY", "1.0")),
            )
            get_llm_service().update_config(new_cfg)
            logger.info(
                f"LLMService 已同步至最新配置: model={new_cfg.model_name}, "
                f"api_base={new_cfg.api_base or '(默认)'}"
            )
        except Exception as e:
            logger.error(f"同步配置到LLMService失败: {e}", exc_info=True)

    async def get_system_config(self) -> Dict[str, Any]:
        """获取系统配置（从缓存读，首次会从DB加载）"""
        await self._ensure_loaded()
        return self._config.copy()

    async def update_system_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新系统配置：
        1. 验证并合并到内存缓存
        2. 持久化到数据库
        3. 同步到LLMService（前端改了模型/API立即生效）
        """
        await self._ensure_loaded()
        logger.info(f"更新系统配置: {list(updates.keys())}")

        applied: Dict[str, Any] = {}
        for key, value in updates.items():
            if key in self._config or key in DEFAULT_CONFIG:
                self._config[key] = _coerce_value(key, value)
                applied[key] = self._config[key]
                logger.info(f"配置项 {key} 已更新")

        if applied:
            await self._persist_to_db(applied)
            # 涉及LLM配置的字段才需要刷新LLM client
            if any(k.startswith("llm_") for k in applied):
                self._apply_to_llm_service()

        return self._config.copy()

    async def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取单个配置项"""
        await self._ensure_loaded()
        return self._config.get(key, default)

    async def set_config_value(self, key: str, value: Any) -> None:
        """设置单个配置项"""
        await self.update_system_config({key: value})

    async def sync_to_llm_service(self) -> None:
        """启动时主动同步配置到LLMService（main.py调用）"""
        await self._ensure_loaded()
        self._apply_to_llm_service()


# 单例实例
_system_config_service: Optional[SystemConfigService] = None


def get_system_config_service() -> SystemConfigService:
    """获取系统配置服务单例"""
    global _system_config_service
    if _system_config_service is None:
        _system_config_service = SystemConfigService()
    return _system_config_service
