# Statistics Service
from typing import List, Optional
import numpy as np
from sqlalchemy import select

from app.config.database import db_config
from app.models import AgentConfig, StrategicGoalEvaluation


class StatisticsService:
    """统计分析服务"""

    async def get_power_history(self, project_id: int, agent_id: Optional[int] = None,
                               start_round: Optional[int] = None,
                               end_round: Optional[int] = None) -> List[dict]:
        """
        获取项目全量智能体国力历史数据
        """
        # TODO: Implement actual database queries
        return []

    async def calculate_power_growth_rate(self, project_id: int, start_round: int = 1,
                                       end_round: Optional[int] = None) -> List[dict]:
        """
        计算自定义轮次区间的实力增长率

        Returns:
            - 相同领导类型+相同实力层级的平均增长率
            - 相同领导类型+不同实力层级的平均增长率
        """
        # TODO: Implement actual calculation logic
        return []

    async def get_action_preference(self, project_id: int, agent_id: Optional[int] = None,
                                  power_level: Optional[str] = None,
                                  leader_type: Optional[str] = None,
                                  start_round: Optional[int] = None,
                                  end_round: Optional[int] = None) -> List[dict]:
        """
        获取行为偏好统计数据

        Returns:
            - 20项互动行为的频次统计
            - 行为分类占比
            - 主权尊重行为占比
            - 高烈度/低烈度行为占比
        """
        # TODO: Implement actual calculation logic
        return []

    async def get_order_evolution(self, project_id: int) -> List[dict]:
        """
        获取国际秩序演变时序数据

        Returns:
            - 每轮的秩序类型
            - 尊重主权率趋势
            - 体系领导权更迭数据
            - 领导国追随率变化
        """
        # TODO: Implement actual database queries
        return []

    async def get_round_detail(self, project_id: int, round_num: int) -> Optional[dict]:
        """
        获取单轮仿真完整详情

        Returns:
            - 本轮所有行为记录
            - 国力变化详情
            - 秩序判定结果
            - 追随关系数据
        """
        # TODO: Implement actual database queries
        return None

    async def get_goal_evaluations(
        self,
        project_id: int,
        agent_id: Optional[int] = None,
        start_round: Optional[int] = None,
        end_round: Optional[int] = None
    ) -> List[dict]:
        """
        获取战略目标评估数据

        Args:
            project_id: 项目ID
            agent_id: 可选，筛选特定智能体
            start_round: 可选，起始轮次
            end_round: 可选，结束轮次

        Returns:
            - 指定轮次区间的评估记录
            - 可按智能体筛选
        """
        async for session in db_config.get_session():
            query = select(StrategicGoalEvaluation, AgentConfig.agent_name).join(
                AgentConfig, StrategicGoalEvaluation.agent_id == AgentConfig.agent_id
            ).where(StrategicGoalEvaluation.project_id == project_id)

            if agent_id is not None:
                query = query.where(StrategicGoalEvaluation.agent_id == agent_id)

            if start_round is not None:
                query = query.where(StrategicGoalEvaluation.evaluation_round >= start_round)

            if end_round is not None:
                query = query.where(StrategicGoalEvaluation.evaluation_round <= end_round)

            query = query.order_by(StrategicGoalEvaluation.evaluation_round, StrategicGoalEvaluation.agent_id)

            result = await session.execute(query)
            rows = result.all()

            return [
                {
                    "evaluation_id": eval.evaluation_id,
                    "agent_id": eval.agent_id,
                    "agent_name": agent_name,
                    "evaluation_round": eval.evaluation_round,
                    "evaluation_round_start": eval.evaluation_round_start,
                    "evaluation_round_end": eval.evaluation_round_end,
                    "goal_achievement_score": eval.goal_achievement_score,
                    "power_growth_contribution": eval.power_growth_contribution,
                    "action_effectiveness": eval.action_effectiveness,
                    "leadership_alignment": eval.leadership_alignment,
                    "overall_assessment": eval.overall_assessment,
                    "specific_achievements": eval.specific_achievements,
                    "challenges": eval.challenges,
                }
                for eval, agent_name in rows
            ]

    async def get_goal_evaluation_trend(
        self,
        project_id: int,
        agent_id: int
    ) -> List[dict]:
        """
        获取单个国家的目标达成度趋势

        Args:
            project_id: 项目ID
            agent_id: 智能体ID

        Returns:
            - 该国所有评估轮次的达成度数据
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(StrategicGoalEvaluation, AgentConfig.agent_name).join(
                    AgentConfig, StrategicGoalEvaluation.agent_id == AgentConfig.agent_id
                ).where(
                    StrategicGoalEvaluation.project_id == project_id,
                    StrategicGoalEvaluation.agent_id == agent_id
                ).order_by(StrategicGoalEvaluation.evaluation_round)
            )
            rows = result.all()

            return [
                {
                    "evaluation_id": eval.evaluation_id,
                    "agent_id": eval.agent_id,
                    "agent_name": agent_name,
                    "evaluation_round": eval.evaluation_round,
                    "evaluation_round_start": eval.evaluation_round_start,
                    "evaluation_round_end": eval.evaluation_round_end,
                    "goal_achievement_score": eval.goal_achievement_score,
                    "power_growth_contribution": eval.power_growth_contribution,
                    "action_effectiveness": eval.action_effectiveness,
                    "leadership_alignment": eval.leadership_alignment,
                    "overall_assessment": eval.overall_assessment,
                    "specific_achievements": eval.specific_achievements,
                    "challenges": eval.challenges,
                }
                for eval, agent_name in rows
            ]


# Singleton instance
statistics_service = StatisticsService()
