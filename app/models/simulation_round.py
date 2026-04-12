"""
SimulationRound model - 仿真轮次表
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


class Base(DeclarativeBase):
    pass


class OrderTypeEnum(str, PyEnum):
    NORMATIVE_ACCEPTANCE = "规范接纳型"
    NON_INTERFERENCE = "不干涉型"
    BIG_STICK_DETERRENCE = "大棒威慑型"
    TERROR_BALANCE = "恐怖平衡型"


class SimulationRound(Base):
    """
    仿真轮次表
    移除用户关联字段，完全对齐学术模型的秩序判定规则，细化核心指标存储。
    """

    __tablename__ = "simulation_round"

    round_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    round_num: Mapped[int] = mapped_column(Integer, nullable=False)
    total_action_count: Mapped[int] = mapped_column(Integer, nullable=False)
    respect_sov_action_count: Mapped[int] = mapped_column(Integer, nullable=False)
    respect_sov_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    has_leader: Mapped[bool] = mapped_column(String(10), nullable=False, default="false")
    leader_agent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    leader_follower_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    order_type: Mapped[str] = mapped_column(String(50), nullable=False)
    round_start_time: Mapped[datetime] = mapped_column(
        type_=func.now(), nullable=False
    )  # SQLite compatibility
    round_end_time: Mapped[datetime] = mapped_column(
        type_=func.now(), nullable=False
    )  # SQLite compatibility

    # Relationships
    project = relationship("SimulationProject", back_populates="rounds")
    actions = relationship("ActionRecord", back_populates="round")
    follower_relations = relationship("FollowerRelation", back_populates="round")

    def __repr__(self) -> str:
        return f"<SimulationRound(id={self.round_id}, round_num={self.round_num}, order_type={self.order_type})>"
