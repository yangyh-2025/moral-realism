"""
预置仿真场景模型 - PresetScene
存储系统提供的预置仿真场景配置，支持一键启动标准化的学术仿真实验。
场景配置包含智能体参数、行为规则等完整信息的JSON格式存储。
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base


class PresetScene(Base):
    """
    预置仿真场景表

    新增核心表，用于存储开箱即用的标准学术仿真场景，实现一键启动能力。

    属性说明：
    - 场景信息：名称、描述、是否为默认场景
    - 仿真配置：总轮次数、智能体配置JSON
    """

    __tablename__ = "preset_scene"

    scene_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scene_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    scene_desc: Mapped[str] = mapped_column(String(2000), nullable=False)
    total_rounds: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_config_json: Mapped[str] = mapped_column(String(10000), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )  # SQLite compatibility
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )  # SQLite compatibility

    def __repr__(self) -> str:
        return f"<PresetScene(id={self.scene_id}, name={self.scene_name}, is_default={self.is_default})>"
