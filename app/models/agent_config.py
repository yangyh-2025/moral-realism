"""
AgentConfig model - 智能体配置表
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Float, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .simulation_project import SimulationProject
    from .action_record import ActionRecord
    from .follower_relation import FollowerRelation
    from .agent_power_history import AgentPowerHistory


class Base(DeclarativeBase):
    pass


class RegionEnum(str, PyEnum):
    AFRICA = "非洲"
    AMERICA = "美洲"
    ASIA = "亚洲"
    EUROPE = "欧洲"
    OCEANIA = "大洋洲"


class PowerLevelEnum(str, PyEnum):
    SUPERPOWER = "超级大国"
    GREAT_POWER = "大国"
    MIDDLE_POWER = "中等强国"
    SMALL_STATE = "小国"


class LeaderTypeEnum(str, PyEnum):
    KINGLY = "王道型"
    HEGEMONIC = "霸权型"
    TYRANICAL = "强权型"
    INEPT = "昏庸型"


class AgentConfig(Base):
    """
    智能体配置表
    核心优化：补全行为权限关联逻辑，移除用户关联字段，强化初始指标与实时国力的隔离，完全对齐学术模型设定。
    """

    __tablename__ = "agent_config"

    agent_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(50), nullable=False)

    # 克莱因国力方程一级初始指标
    c_score: Mapped[float] = mapped_column(Float, nullable=False)  # 基本实体 (0-100)
    e_score: Mapped[float] = mapped_column(Float, nullable=False)  # 经济实力 (0-200)
    m_score: Mapped[float] = mapped_column(Float, nullable=False)  # 军事实力 (0-200)
    s_score: Mapped[float] = mapped_column(Float, nullable=False)  # 战略目的 (0-2)
    w_score: Mapped[float] = mapped_column(Float, nullable=False)  # 国家战略意志 (0-2)

    # 自动计算字段
    initial_total_power: Mapped[float] = mapped_column(Float, nullable=False)
    current_total_power: Mapped[float] = mapped_column(Float, nullable=False)
    power_level: Mapped[str] = mapped_column(String(50), nullable=False)

    # 领导集体类型（仅超级大国/大国可配置）
    leader_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        type_=func.now(), nullable=False
    )  # SQLite compatibility
    updated_at: Mapped[datetime] = mapped_column(
        type_=func.now(), nullable=False, server_default=func.now()
    )  # SQLite compatibility

    # Relationships
    project = relationship("SimulationProject", back_populates="agents")
    initiated_actions = relationship("ActionRecord", foreign_keys="ActionRecord.source_agent_id", back_populates="source_agent")
    targetted_actions = relationship("ActionRecord", foreign_keys="ActionRecord.target_agent_id", back_populates="target_agent")
    follower_relations = relationship("FollowerRelation", back_populates="agent")
    power_histories = relationship("AgentPowerHistory", back_populates="agent")

    def __repr__(self) -> str:
        return f"<AgentConfig(id={self.agent_id}, name={self.agent_name}, power_level={self.power_level})>"
