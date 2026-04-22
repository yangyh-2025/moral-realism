"""
战略目标评估模型 - StrategicGoalEvaluation
用于评估智能体在一段时间内的战略目标达成情况。
每隔一定轮次（默认10轮）对每个智能体的目标达成度进行综合评估。
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..models import Base

if TYPE_CHECKING:
    from .simulation_project import SimulationProject
    from .agent_config import AgentConfig


class StrategicGoalEvaluation(Base):
    """
    战略目标评估记录表

    存储每10轮对每个国家的战略目标达成度评估结果。

    属性说明：
    - 项目/智能体关联：所属项目和智能体
    - 评估轮次信息：评估时的轮次、评估区间起始和结束轮次
    - 评估结果：综合目标达成度、国力增长贡献度、行为有效性、领导类型一致性
    - 评估说明：综合评估说明、具体成就、面临挑战
    """

    __tablename__ = "strategic_goal_evaluation"

    evaluation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("simulation_project.project_id"), nullable=False, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent_config.agent_id"), nullable=False, index=True)

    # 评估轮次信息
    evaluation_round: Mapped[int] = mapped_column(Integer, nullable=False)  # 评估时的轮次
    evaluation_round_start: Mapped[int] = mapped_column(Integer, nullable=False)  # 评估区间起始轮次
    evaluation_round_end: Mapped[int] = mapped_column(Integer, nullable=False)  # 评估区间结束轮次

    # 评估结果 (0-100)
    goal_achievement_score: Mapped[float] = mapped_column(Float, nullable=False)  # 综合目标达成度
    power_growth_contribution: Mapped[float] = mapped_column(Float, nullable=True)  # 国力贡献度（数据驱动Min-Max标准化）
    action_effectiveness: Mapped[float] = mapped_column(Float, nullable=True)  # 行为有效性（LLM评分）
    leadership_alignment: Mapped[float] = mapped_column(Float, nullable=True)  # 领导类型一致性（已废弃）

    # 评估说明
    overall_assessment: Mapped[str] = mapped_column(String(1000), nullable=True)  # 综合评估说明
    specific_achievements: Mapped[str] = mapped_column(String(2000), nullable=True)  # 具体成就
    challenges: Mapped[str] = mapped_column(String(2000), nullable=True)  # 面临挑战

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    # Relationships
    project = relationship("SimulationProject", back_populates="goal_evaluations")
    agent = relationship("AgentConfig", back_populates="goal_evaluations")

    def __repr__(self) -> str:
        return f"<StrategicGoalEvaluation(id={self.evaluation_id}, agent_id={self.agent_id}, round={self.evaluation_round}, score={self.goal_achievement_score})>"
