"""
战略关系模型 - StrategicRelationship
用于存储国家之间的双边战略关系等级。
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base

if TYPE_CHECKING:
    from .agent_config import AgentConfig
    from .simulation_project import SimulationProject


class StrategicRelationshipEnum(str, PyEnum):
    """战略关系枚举类型

    定义两国之间的双边战略关系，从敌对到友好的五级分类。
    """
    WAR = "战争关系"
    CONFLICT = "冲突关系"
    NO_DIPLOMACY = "无外交关系"
    PARTNERSHIP = "伙伴关系"
    ALLIANCE = "盟友关系"


class StrategicRelationship(Base):
    """
    战略关系表

    存储智能体之间的双边战略关系等级。

    约束规则：
    - source_agent_id < target_agent_id，避免重复存储
    - 存储大国/超级大国与中小国家之间的战略关系

    允许的配对组合：
    - 超级大国 × 大国
    - 超级大国 × 中等强国
    - 超级大国 × 小国
    - 大国 × 中等强国
    - 大国 × 小国

    不建立关系的组合：
    - 中等强国 × 中等强国
    - 中等强国 × 小国
    - 小国 × 小国
    """
    __tablename__ = "strategic_relationship"

    relation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("simulation_project.project_id"), nullable=False, index=True)
    source_agent_id: Mapped[int] = mapped_column(ForeignKey("agent_config.agent_id"), nullable=False, index=True)
    target_agent_id: Mapped[int] = mapped_column(ForeignKey("agent_config.agent_id"), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("SimulationProject", back_populates="strategic_relationships")

    def __repr__(self) -> str:
        return f"<StrategicRelationship(source={self.source_agent_id}, target={self.target_agent_id}, type={self.relationship_type})>"
