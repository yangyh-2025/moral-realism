"""
仿真轮次模型 - SimulationRound
记录仿真过程中每个轮次的关键指标，包括秩序类型、尊重主权比例、
领导者信息等，用于分析国际秩序的演变过程研究。
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


class OrderTypeEnum(str, PyEnum):
    """国际秩序类型枚举

    定义根据学术模型判定的四种国际秩序类型。
    """
    NORMATIVE_ACCEPTANCE = "规范接纳型"
    NON_INTERFERENCE = "不干涉型"
    BIG_STICK_DETERRENCE = "大棒威慑型"
    TERROR_BALANCE = "恐怖平衡型"


class SimulationRound(Base):
    """
    仿真轮次表

    移除用户关联字段，完全对齐学术模型的秩序判定规则，细化核心指标存储。

    属性说明：
    - 项目/轮次关联：所属项目和轮次编号
    - 行为统计：总行为数、尊重主权行为数、尊重主权比例
    - 领导权信息：是否存在领导者、领导者ID、领导者追随比例
    - 秩序类型：规范接纳型/不干涉型/大棒威慑型/恐怖平衡型
    - 时间信息：轮次开始和结束时间
    """

    __tablename__ = "simulation_round"

    round_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("simulation_project.project_id"), nullable=False, index=True)
    round_num: Mapped[int] = mapped_column(Integer, nullable=False)
    total_action_count: Mapped[int] = mapped_column(Integer, nullable=False)
    respect_sov_action_count: Mapped[int] = mapped_column(Integer, nullable=False)
    respect_sov_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    has_leader: Mapped[bool] = mapped_column(String(10), nullable=False, default="false")
    leader_agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agent_config.agent_id"), nullable=True)
    leader_follower_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    order_type: Mapped[str] = mapped_column(String(50), nullable=False)
    round_start_time: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )  # SQLite compatibility
    round_end_time: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )  # SQLite compatibility

    # Relationships
    project = relationship("SimulationProject", back_populates="rounds")
    actions = relationship("ActionRecord", back_populates="round")
    follower_relations = relationship("FollowerRelation", back_populates="round")

    def __repr__(self) -> str:
        return f"<SimulationRound(id={self.round_id}, round_num={self.round_num}, order_type={self.order_type})>"
