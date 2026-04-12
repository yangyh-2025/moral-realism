"""
Database configuration and initialization for the ABM simulation system.
"""

import json
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database URL - using SQLite with async support
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR}/abm_simulation.db"


class DatabaseConfig:
    """Database configuration class"""

    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url
        self._engine: AsyncEngine | None = None
        self._async_session_factory: async_sessionmaker | None = None

    @property
    def engine(self) -> AsyncEngine:
        """Get or create database engine"""
        if self._engine is None:
            self._engine = create_async_engine(
                self.db_url,
                echo=False,
                future=True,
                connect_args={"check_same_thread": False},
            )
        return self._engine

    @property
    def async_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create async session factory"""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
        return self._async_session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close database connections"""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._async_session_factory = None


# Global database instance
db_config = DatabaseConfig()


async def init_database() -> None:
    """Initialize database tables"""
    from app.models import Base

    async with db_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_default_data() -> None:
    """Initialize default data: action configs, preset scenes, system config"""
    from app.models import (
        ActionConfig,
        PresetScene,
        SystemConfig,
    )

    async for session in db_config.get_session():
        # Initialize action configs if empty
        action_count = await session.execute(
            "SELECT COUNT(*) FROM action_config"
        )
        if action_count.scalar() == 0:
            await _init_action_configs(session)

        # Initialize preset scenes if empty
        scene_count = await session.execute(
            "SELECT COUNT(*) FROM preset_scene"
        )
        if scene_count.scalar() == 0:
            await _init_preset_scenes(session)

        # Initialize system config if empty
        config_count = await session.execute(
            "SELECT COUNT(*) FROM system_config"
        )
        if config_count.scalar() == 0:
            await _init_system_config(session)


async def _init_action_configs(session: AsyncSession) -> None:
    """Initialize 20 standard interaction actions from academic model"""
    from app.models import ActionConfig

    actions = [
        {
            "action_name": "发表公开声明",
            "action_en_name": "MAKE PUBLIC STATEMENT",
            "action_category": "外交手段",
            "action_desc": "发表针对国际事务的公开声明或讲话，表达国家立场",
            "respect_sov": True,
            "initiator_power_change": 0,
            "target_power_change": 0,
            "is_initiative": True,
            "is_response": True,
            "allowed_initiator_level": json.dumps([
                "超级大国", "大国", "中等强国", "小国"
            ]),
            "allowed_responder_level": json.dumps([
                "超级大国", "大国", "中等强国", "小国"
            ]),
            "forbidden_leader_type": json.dumps([]),
        },
        {
            "action_name": "呼吁/请求",
            "action_en_name": "APPEAL",
            "action_category": "外交手段",
            "action_desc": "向其他国家发出呼吁或请求，寻求支持或合作",
            "respect_sov": True,
            "initiator_power_change": 1,
            "target_power_change": 0,
            "is_initiative": True,
            "is_response": False,
            "allowed_initiator_level": json.dumps([
                "超级大国", "大国", "中等强国", "小国"
            ]),
            "allowed_responder_level": json.dumps([
                "超级大国", "大国", "中等强国", "小国"
            ]),
            "forbidden_leader_type": json.dumps([]),
        }
    ]
    ]

    for action_data in actions:
        action = ActionConfig(**action_data)
        session.add(action)


async def _init_preset_scenes(session: AsyncSession) -> None:
    """Initialize default preset scenes"""
    # Will be implemented with 3 classic academic scenes
    pass


async def _init_system_config(session: AsyncSession) -> None:
    """Initialize default system configuration"""
    from app.models import SystemConfig

    configs = [
        {
            "config_key": "llm_model_name",
            "config_value": "gpt-4-turbo",
            "config_desc": "LLM模型名称",
        },
        {
            "config_key": "llm_api_key",
            "config_value": "",
            "config_desc": "LLM API密钥",
        },
        {
            "config_key": "llm_timeout",
            "config_value": "60",
            "config_desc": "LLM调用超时时间（秒）",
        },
        {
            "config_key": "llm_max_retries",
            "config_value": "3",
            "config_desc": "LLM调用最大重试次数",
        },
        {
            "config_key": "simulation_concurrency",
            "config_value": "5",
            "config_desc": "仿真并发数",
        },
        {
            "config_key": "log_level",
            "config_value": "INFO",
            "config_desc": "日志级别",
        },
        {
            "config_key": "default_scene_id",
            "config_value": "1",
            "config_desc": "默认场景ID",
        },
    ]

    for config_data in configs:
        config = SystemConfig(**config_data)
        session.add(config)
