"""
智能体配置模型 - AgentConfig (CINC版)
用于存储智能体的基础信息、CINC国力指标、领导类型等配置数据。
智能体是仿真系统中的基本行为主体，代表不同的国家或政治实体。

CINC替换说明：
- 移除旧版5指标（c_score, e_score, m_score, s_score, w_score），替换为CINC底层6指标（milex, milper, irst, pec, tpop, upop）
- initial_total_power 与 current_total_power 含义变为 CINC指数（0-1的比例值）
- 新增 cinc_year 字段记录数据来源年份
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base

if TYPE_CHECKING:
    from .simulation_project import SimulationProject
    from .action_record import ActionRecord
    from .follower_relation import FollowerRelation
    from .agent_power_history import AgentPowerHistory


class RegionEnum(str, PyEnum):
    """地理区域枚举类型"""
    AFRICA = "非洲"
    AMERICA = "美洲"
    ASIA = "亚洲"
    EUROPE = "欧洲"
    OCEANIA = "大洋洲"


class PowerLevelEnum(str, PyEnum):
    """国力等级枚举类型（基于CINC在仿真体系内排名）"""
    SUPERPOWER = "超级大国"
    GREAT_POWER = "大国"
    MIDDLE_POWER = "中等强国"
    SMALL_STATE = "小国"


class LeaderTypeEnum(str, PyEnum):
    """领导类型枚举类型"""
    KINGLY = "王道型"
    HEGEMONIC = "霸权型"
    TYRANICAL = "强权型"
    INEPT = "昏庸型"


class AgentConfig(Base):
    """
    智能体配置表（CINC版）

    属性说明：
    - 基础信息：名称、所属区域、国力等级
    - CINC底层6指标：军事支出、军事人员、钢铁产量、能源消耗、总人口、城市人口
    - 自动计算字段：初始CINC、当前CINC、国力等级
    - 数据来源：CINC年份、COW国家代码（可选）
    - 领导类型：仅超级大国/大国可配置
    """

    __tablename__ = "agent_config"

    agent_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("simulation_project.project_id"), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(50), nullable=False)

    # CINC底层6项指标
    milex: Mapped[float] = mapped_column(Float, nullable=False, default=0)  # 军事支出（千美元）
    milper: Mapped[float] = mapped_column(Float, nullable=False, default=0)  # 军事人员（千人）
    irst: Mapped[float] = mapped_column(Float, nullable=False, default=0)   # 钢铁产量（千吨）
    pec: Mapped[float] = mapped_column(Float, nullable=False, default=0)    # 一次能源消耗（千吨煤当量）
    tpop: Mapped[float] = mapped_column(Float, nullable=False, default=0)   # 总人口（千人）
    upop: Mapped[float] = mapped_column(Float, nullable=False, default=0)   # 城市人口（千人）

    # CINC综合国力指数（自动计算字段，含义为体系内CINC比例值0-1）
    initial_total_power: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_total_power: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    power_level: Mapped[str] = mapped_column(String(50), nullable=False, default="小国")

    # 数据来源标记（可选）
    cinc_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=2016)
    country_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # COW数字代码

    # 领导集体类型（仅超级大国/大国可配置）
    leader_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    project = relationship("SimulationProject", back_populates="agents")
    initiated_actions = relationship("ActionRecord", foreign_keys="ActionRecord.source_agent_id", back_populates="source_agent")
    targetted_actions = relationship("ActionRecord", foreign_keys="ActionRecord.target_agent_id", back_populates="target_agent")
    follower_relations = relationship("FollowerRelation", foreign_keys="FollowerRelation.follower_agent_id", back_populates="agent")
    power_histories = relationship("AgentPowerHistory", back_populates="agent")
    goal_evaluations = relationship("StrategicGoalEvaluation", back_populates="agent")

    def __repr__(self) -> str:
        return f"<AgentConfig(id={self.agent_id}, name={self.agent_name}, cinc={self.current_total_power:.4f}, level={self.power_level})>"
