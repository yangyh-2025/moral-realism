"""
互动行为记录模型 - ActionRecord
记录智能体在仿真过程中的实际互动行为，包括行为类型、发起方、目标方、
行为阶段等信息，以及行为对双方国力的影响。
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
    """行为阶段枚举

    定义互动行为的两个阶段：发起阶段和响应阶段。
    """
    INITIATIVE = "发起阶段"
    RESPONSE = "响应阶段"


class ActionRecord(Base):
    """
    互动行为记录表

    核心优化：与20项互动行为集强绑定，补全行为全属性记录，移除用户关联字段。

    属性说明：
    - 项目/轮次关联：所属项目和具体轮次
    - 行为信息：行为阶段、发起方、目标方、行为类型
    - 行为属性：是否尊重主权、对双方国力的影响
    - 决策详情：LLM 决策过程的详细记录
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
