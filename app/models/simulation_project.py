"""
仿真项目模型 - SimulationProject
仿真项目是系统的核心实体，代表一次完整的仿真实验。
包含项目配置、运行状态、场景来源等信息，并关联所有相关的仿真数据。
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
    """仿真项目状态枚举

    定义仿真项目可能处于的不同状态。
    """
    NOT_STARTED = "未启动"
    RUNNING = "运行中"
    PAUSED = "暂停"
    COMPLETED = "已完成"
    TERMINATED = "已终止"


class SimulationProject(Base):
    """
    仿真项目主表

    移除用户关联字段，固定学术阈值，新增场景来源字段，适配预置场景一键启动能力。

    属性说明：
    - 基础信息：项目名称、描述、场景来源
    - 仿真配置：总轮数、当前轮次、运行状态
    - 学术阈值：尊重主权阈值、领导权阈值（均固定为60%）
    - 关联关系：智能体、轮次、行为记录、追随关系、国力历史、目标评估
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
    goal_evaluations = relationship(
        "StrategicGoalEvaluation", back_populates="project", cascade="all, delete-orphan"
    )
    strategic_relationships = relationship(
        "StrategicRelationship", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SimulationProject(id={self.project_id}, name={self.project_name}, status={self.status})>"
