"""
FollowerRelation model - 智能体追随关系表
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .simulation_project import SimulationProject
    from .simulation_round import SimulationRound
    from .agent_config import AgentConfig


class Base(DeclarativeBase):
    pass


class FollowerRelation(Base):
    """
    智能体追随关系表
    移除用户关联字段，完全对齐学术模型的领导权判定规则。
    """

    __tablename__ = "follower_relation"

    relation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    round_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    round_num: Mapped[int] = mapped_column(Integer, nullable=False)
    follower_agent_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    leader_agent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        type_=func.now(), nullable=False
    )  # SQLite compatibility

    # Relationships
    project = relationship("SimulationProject", back_populates="follower_relations")
    round = relationship("SimulationRound", back_populates="follower_relations")
    agent = relationship("AgentConfig", back_populates="follower_relations")

    def __repr__(self) -> str:
        return f"<FollowerRelation(id={self.relation_id}, follower={self.follower_agent_id}, leader={self.leader_agent_id})>"
