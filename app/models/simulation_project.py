"""
SimulationProject model - 仿真项目主表
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base


class ProjectStatus(str, PyEnum):
    NOT_STARTED = "未启动"
    RUNNING = "运行中"
    PAUSED = "暂停"
    COMPLETED = "已完成"
    TERMINATED = "已终止"


class SimulationProject(Base):
    """
    仿真项目主表
    移除用户关联字段，固定学术阈值，新增场景来源字段，适配预置场景一键启动能力。
    """

    __tablename__ = "simulation_project"

    project_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scene_source: Mapped[str] = mapped_column(
        String(100), nullable=False, default="自定义"
    )
    total_rounds: Mapped[int] = mapped_column(Integer, nullable=False)
    current_round: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="未启动")
    respect_sov_threshold: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.6
    )  # 学术模型固定60%
    leader_threshold: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.6
    )  # 学术模型固定60%
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    agents = relationship("AgentConfig", back_populates="project", cascade="all, delete-orphan")
    rounds = relationship("SimulationRound", back_populates="project", cascade="all, delete-orphan")
    actions = relationship("ActionRecord", back_populates="project", cascade="all, delete-orphan")
    follower_relations = relationship(
        "FollowerRelation", back_populates="project", cascade="all, delete-orphan"
    )
    power_histories = relationship(
        "AgentPowerHistory", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SimulationProject(id={self.project_id}, name={self.project_name}, status={self.status})>"
