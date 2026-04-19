"""
系统配置管理服务
负责全局系统配置的读取和更新
"""

from typing import Dict, Any, Optional
import os
from loguru import logger


class SystemConfigService:
    """系统配置管理服务"""

    def __init__(self):
        """
        初始化系统配置服务

        从环境变量加载配置，或使用默认值。
        """
        self._config: Dict[str, Any] = {
            "llm_model_name": os.getenv("LLM_MODEL", "gpt-4"),
            "llm_api_key": os.getenv("OPENAI_API_KEY", ""),
            "llm_api_base": os.getenv("OPENAI_API_BASE", None),
            "llm_timeout": int(os.getenv("LLM_TIMEOUT", "60")),
            "llm_max_retries": int(os.getenv("LLM_MAX_RETRIES", "3")),
            "simulation_concurrency": 5,
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "default_scene_id": 1
        }

    async def get_system_config(self) -> Dict[str, Any]:
        """
        获取系统配置

        返回当前系统配置的副本。

        Returns:
            系统配置字典
        """
        logger.info("正在获取系统配置")
        return self._config.copy()

    async def update_system_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新系统配置

        更新指定的配置项。

        Args:
            updates: 需要更新的配置项字典

        Returns:
            更新后的系统配置字典
        """
        logger.info(f"正在更新系统配置: {updates}")
        for key, value in updates.items():
            if key in self._config:
                self._config[key] = value
                logger.info(f"配置项 {key} 已更新为 {value}")
        return self._config.copy()

    async def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取单个配置项

        Args:
            key: 配置项名称
            default: 默认值

        Returns:
            配置项的值
        """
        return self._config.get(key, default)

    async def set_config_value(self, key: str, value: Any) -> None:
        """
        设置单个配置项

        Args:
            key: 配置项名称
            value: 配置项的值
        """
        await self.update_system_config({key: value})


# 单例实例
_system_config_service: Optional[SystemConfigService] = None


def get_system_config_service() -> SystemConfigService:
    """
    获取系统配置服务单例

    使用单例模式确保整个应用共享同一个配置服务实例。

    Returns:
        SystemConfigService单例实例
    """
    global _system_config_service
    if _system_config_service is None:
        _system_config_service = SystemConfigService()
    return _system_config_service
