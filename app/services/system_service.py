# System Config Service
from typing import Dict, Any, Optional
from loguru import logger


class SystemConfigService:
    """系统配置管理服务"""

    def __init__(self):
        """Initialize with default configuration"""
        self._config: Dict[str, Any] = {
            "llm_model_name": "gpt-4",
            "llm_api_key": "",
            "llm_api_base": None,
            "llm_timeout": 120,
            "llm_max_retries": 3,
            "simulation_concurrency": 5,
            "log_level": "INFO",
            "default_scene_id": 1
        }

    async def get_system_config(self) -> Dict[str, Any]:
        """
        获取系统配置
        """
        logger.info("Fetching system config")
        return self._config.copy()

    async def update_system_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新系统配置
        """
        logger.info(f"Updating system config with: {updates}")
        for key, value in updates.items():
            if key in self._config:
                self._config[key] = value
                logger.info(f"Updated config {key} = {value}")
        return self._config.copy()

    async def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取单个配置项
        """
        return self._config.get(key, default)

    async def set_config_value(self, key: str, value: Any) -> None:
        """
        设置单个配置项
        """
        await self.update_system_config({key: value})


# Singleton instance
_system_config_service: Optional[SystemConfigService] = None


def get_system_config_service() -> SystemConfigService:
    """获取系统配置服务单例"""
    global _system_config_service
    if _system_config_service is None:
        _system_config_service = SystemConfigService()
    return _system_config_service
