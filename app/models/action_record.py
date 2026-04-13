"""
ActionRecord model - 互动行为记录表
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base

if TYPE_CHECKING:
    from .simulation_project import SimulationProject
    from .simulation_round import SimulationRound
    from .agent_config import AgentConfig
    from .action_config import ActionConfig


class ActionStageEnum(str, PyEnum):
    INITIATIVE = "发起阶段"
    RESPONSE = "响应阶段"


class ActionRecord(Base):
    """
    互动行为记录表
    核心优化：与20项互动行为集强绑定，补全行为全属性记录，移除用户关联字段。
    """

    __tablename__ = "action_record"

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("simulation_project.project_id"), nullable=False, index=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("simulation_round.round_id"), nullable=False, index=True)
    round_num: Mapped[int] = mapped_column(Integer, nullable=False)
    action_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    source_agent_id: Mapped[int] = mapped_column(ForeignKey("agent_config.agent_id"), nullable=False, index=True)
    target_agent_id: Mapped[int] = mapped_column(ForeignKey("agent_config.agent_id"), nullable=False, index=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("action_config.action_id"), nullable=False, index=True)
    action_category: Mapped[str] = mapped_column(String(50), nullable=False)
    action_name: Mapped[str] = mapped_column(String(255), nullable=False)
    respect_sov: Mapped[bool] = mapped_column(String(10), nullable=False, default="false")
    initiator_power_change: Mapped[int] = mapped_column(Integer, nullable=False)
    target_power_change: Mapped[int] = mapped_column(Integer, nullable=False)
    decision_detail: Mapped[str] = mapped_column(String(5000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )  # SQLite compatibility

    # Relationships
    project = relationship("SimulationProject", back_populates="actions")
    round = relationship("SimulationRound", back_populates="actions")
    source_agent = relationship("AgentConfig", foreign_keys=[source_agent_id], back_populates="initiated_actions")
    target_agent = relationship("AgentConfig", foreign_keys=[target_agent_id], back_populates="targetted_actions")
    action_config = relationship("ActionConfig", back_populates="action_records")

    def __repr__(self) -> str:
        return f"<ActionRecord(id={self.record_id}, action={self.action_name}, stage={self.action_stage})>"
