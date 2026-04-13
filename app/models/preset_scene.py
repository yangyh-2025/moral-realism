"""
PresetScene model - 预置仿真场景表
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base


class PresetScene(Base):
    """
    预置仿真场景表
    新增核心表，用于存储开箱即用的标准学术仿真场景，实现一键启动能力。
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
