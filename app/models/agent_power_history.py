"""
AgentPowerHistory model - 智能体国力历史表
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .simulation_project import SimulationProject
    from .agent_config import AgentConfig
    from .simulation_round import SimulationRound


class Base(DeclarativeBase):
    pass


class AgentPowerHistory(Base):
    """
    智能体国力历史表
    移除用户关联字段，完整记录每轮仿真后智能体的国力数据，满足学术观测要求。
    """

    __tablename__ = "agent_power_history"

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    round_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    round_num: Mapped[int] = mapped_column(Integer, nullable=False)
    round_start_power: Mapped[float] = mapped_column(Float, nullable=False)
    round_end_power: Mapped[float] = mapped_column(Float, nullable=False)
    round_change_value: Mapped[float] = mapped_column(Float, nullable=False)
    round_change_rate: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        type_=func.now(), nullable=False
    )  # SQLite compatibility

    # Relationships
    project = relationship("SimulationProject", back_populates="power_histories")
    agent = relationship("AgentConfig", back_populates="power_histories")

    def __repr__(self) -> str:
        return f"<AgentPowerHistory(id={self.history_id}, agent_id={self.agent_id}, round={self.round_num})>"
