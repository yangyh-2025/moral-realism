"""
智能体国力历史模型 - AgentPowerHistory
用于记录智能体在每轮仿真中的国力变化过程，包括起始国力、结束国力、
变化值和变化率。这些数据对于分析仿真过程中的国力动态至关重要。
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base

if TYPE_CHECKING:
    from .simulation_project import SimulationProject
    from .agent_config import AgentConfig
    from .simulation_round import SimulationRound


class AgentPowerHistory(Base):
    """
    智能体国力历史表

    移除用户关联字段，完整记录每轮仿真后智能体的国力数据，满足学术观测要求。

    属性说明：
    - 项目/智能体/轮次关联：所属项目、智能体和具体轮次
    - 国力数据：起始国力、结束国力、变化值、变化率
    """

    __tablename__ = "agent_power_history"

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("simulation_project.project_id"), nullable=False, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent_config.agent_id"), nullable=False, index=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("simulation_round.round_id"), nullable=False, index=True)
    round_num: Mapped[int] = mapped_column(Integer, nullable=False)
    round_start_power: Mapped[float] = mapped_column(Float, nullable=False)
    round_end_power: Mapped[float] = mapped_column(Float, nullable=False)
    round_change_value: Mapped[float] = mapped_column(Float, nullable=False)
    round_change_rate: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )  # SQLite compatibility

    # Relationships
    project = relationship("SimulationProject", back_populates="power_histories")
    agent = relationship("AgentConfig", back_populates="power_histories")

    def __repr__(self) -> str:
        return f"<AgentPowerHistory(id={self.history_id}, agent_id={self.agent_id}, round={self.round_num})>"
