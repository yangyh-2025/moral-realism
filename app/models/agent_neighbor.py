"""
邻接关系模型 - AgentNeighbor
用于存储两个智能体之间的二元邻接关系(是否为邻国)。

与 strategic_relationship 不同:
- 仅有一个布尔字段 is_neighbor (无 enum)
- 适用于所有智能体对子, 不受 power_level 限制
- 采用 source_agent_id < target_agent_id 的无向存储
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base

if TYPE_CHECKING:
    from .agent_config import AgentConfig
    from .simulation_project import SimulationProject


class AgentNeighbor(Base):
    """
    邻接关系表

    存储智能体之间是否互为邻国的二元关系。

    约束规则:
    - source_agent_id < target_agent_id, 避免重复存储 (无向关系)
    - 所有智能体对子均可建立记录, 不受 power_level 限制
    - 每个项目内 (project_id, source_agent_id, target_agent_id) 唯一
    """
    __tablename__ = "agent_neighbor"
    __table_args__ = (
        UniqueConstraint(
            'project_id', 'source_agent_id', 'target_agent_id',
            name='uq_agent_neighbor'
        ),
    )

    relation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("simulation_project.project_id"), nullable=False, index=True)
    source_agent_id: Mapped[int] = mapped_column(ForeignKey("agent_config.agent_id"), nullable=False, index=True)
    target_agent_id: Mapped[int] = mapped_column(ForeignKey("agent_config.agent_id"), nullable=False, index=True)
    is_neighbor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("SimulationProject", back_populates="agent_neighbors")

    def __repr__(self) -> str:
        return f"<AgentNeighbor(source={self.source_agent_id}, target={self.target_agent_id}, is_neighbor={self.is_neighbor})>"
