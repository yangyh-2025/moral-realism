"""
Strategic Goal Evaluation Service
使用 LLM 驱动的评估智能体，评估每个国家的战略目标达成度
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import db_config
from app.services.llm_service import get_llm_service
from app.models import (
    AgentConfig,
    ActionRecord,
    AgentPowerHistory,
    StrategicGoalEvaluation,
)
from loguru import logger


class GoalEvaluationService:
    """战略目标评估服务"""

    def __init__(self):
        # 复用现有的 LLM 服务，与其他智能体共享相同的 LLM API
        self.llm_service = get_llm_service()

    async def evaluate_agent_goal_achievement(
        self,
        project_id: int,
        agent_id: int,
        evaluation_round: int,
        evaluation_window: int = 10
    ) -> dict:
        """
        评估单个国家在最近N轮的战略目标达成度

        Args:
            project_id: 项目ID
            agent_id: 智能体ID
            evaluation_round: 当前轮次
            evaluation_window: 评估窗口（默认10轮）

        Returns:
            评估结果字典
        """
        start_round = max(1, evaluation_round - evaluation_window + 1)

        # 1. 收集数据
        agent_info = await self._get_agent_info(project_id, agent_id)
        action_records = await self._get_action_records(project_id, agent_id, start_round, evaluation_round)
        power_history = await self._get_power_history(project_id, agent_id, start_round, evaluation_round)

        # 2. 构建评估提示词
        prompt = self._build_evaluation_prompt(
            agent_info, action_records, power_history, start_round, evaluation_round
        )

        # 3. 调用 LLM 进行评估
        try:
            evaluation_result = await self.llm_service.call_llm_async(
                prompt=prompt,
                system_prompt=self._get_evaluation_system_prompt()
            )
            logger.info(f"Agent {agent_id} evaluation completed at round {evaluation_round}")
        except Exception as e:
            logger.error(f"Agent {agent_id} evaluation failed: {e}")
            # 返回默认评估结果
            evaluation_result = {
                "goal_achievement_score": 50.0,
                "power_growth_contribution": 50.0,
                "action_effectiveness": 50.0,
                "leadership_alignment": 50.0,
                "overall_assessment": f"评估失败: {str(e)}",
                "specific_achievements": "无",
                "challenges": "评估服务异常"
            }

        # 4. 保存评估结果
        await self._save_evaluation_result(
            project_id, agent_id, evaluation_round, start_round, evaluation_round, evaluation_result
        )

        return evaluation_result

    async def _get_agent_info(self, project_id: int, agent_id: int) -> Optional[dict]:
        """获取智能体信息"""
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(
                    AgentConfig.project_id == project_id,
                    AgentConfig.agent_id == agent_id
                )
            )
            agent = result.scalar_one_or_none()

            if not agent:
                return None

            # 从 AgentBase 获取国家利益偏好
            from app.core.agent_base import AgentBase
            agent_base = AgentBase(**{
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "region": agent.region,
                "c_score": agent.c_score,
                "e_score": agent.e_score,
                "m_score": agent.m_score,
                "s_score": agent.s_score,
                "w_score": agent.w_score,
                "initial_total_power": agent.initial_total_power,
                "current_total_power": agent.current_total_power,
                "power_level": agent.power_level,
                "leader_type": agent.leader_type,
            })

            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "region": agent.region,
                "power_level": agent.power_level,
                "leader_type": agent.leader_type or "无",
                "initial_total_power": agent.initial_total_power,
                "current_total_power": agent.current_total_power,
                "national_interest": agent_base.national_interest,
            }

    async def _get_action_records(
        self, project_id: int, agent_id: int, start_round: int, end_round: int
    ) -> List[dict]:
        """获取行为记录"""
        async for session in db_config.get_session():
            result = await session.execute(
                select(ActionRecord).where(
                    ActionRecord.project_id == project_id,
                    ActionRecord.source_agent_id == agent_id,
                    ActionRecord.round_num >= start_round,
                    ActionRecord.round_num <= end_round
                )
            )
            records = result.scalars().all()

            return [
                {
                    "round_num": r.round_num,
                    "action_name": r.action_name,
                    "action_category": r.action_category,
                    "respect_sov": r.respect_sov,
                    "initiator_power_change": r.initiator_power_change,
                    "target_power_change": r.target_power_change,
                }
                for r in records
            ]

    async def _get_power_history(
        self, project_id: int, agent_id: int, start_round: int, end_round: int
    ) -> List[dict]:
        """获取国力历史"""
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentPowerHistory).where(
                    AgentPowerHistory.project_id == project_id,
                    AgentPowerHistory.agent_id == agent_id,
                    AgentPowerHistory.round_num >= start_round,
                    AgentPowerHistory.round_num <= end_round
                )
            )
            records = result.scalars().all()

            return [
                {
                    "round_num": r.round_num,
                    "round_start_power": r.round_start_power,
                    "round_end_power": r.round_end_power,
                    "round_change_value": r.round_change_value,
                    "round_change_rate": r.round_change_rate,
                }
                for r in records
            ]

    def _build_evaluation_prompt(
        self, agent_info, action_records, power_history, start_round, end_round
    ) -> str:
        """构建评估提示词"""
        # 行为记录统计
        total_actions = len(action_records)
        respect_sov_count = sum(1 for r in action_records if r["respect_sov"])
        respect_sov_ratio = respect_sov_count / total_actions if total_actions > 0 else 0

        # 行为类别统计
        from collections import Counter
        action_categories = Counter(r["action_category"] for r in action_records)

        # 国力变化统计
        total_power_change = sum(r["round_change_value"] for r in power_history)
        avg_power_change = total_power_change / len(power_history) if power_history else 0

        prompt = f"""请评估以下国家在最近{end_round - start_round + 1}轮仿真中的战略目标达成情况。

【国家基本信息】
- 国家名称: {agent_info['agent_name']}
- 所属区域: {agent_info['region']}
- 实力层级: {agent_info['power_level']}
- 领导类型: {agent_info['leader_type']}
- 初始综合国力: {agent_info['initial_total_power']:.2f}
- 当前综合国力: {agent_info['current_total_power']:.2f}

【国家利益偏好】
{chr(10).join(f"- {interest}" for interest in agent_info['national_interest'])}

【行为统计（第{start_round}-{end_round}轮）】
- 总行为数: {total_actions}
- 尊重主权行为数: {respect_sov_count}
- 尊重主权率: {respect_sov_ratio:.2%}
- 国力总变化: {total_power_change:.2f}
- 平均轮次国力变化: {avg_power_change:.2f}

【行为类别分布】
{chr(10).join(f"- {cat}: {count}" for cat, count in action_categories.items())()}

【国力变化详情】
{chr(10).join(f"第{r['round_num']}轮: {r['round_start_power']:.2f} → {r['round_end_power']:.2f} (变化: {r['round_change_value']:.2f}, 增长率: {r['round_change_rate']:.2%})" for r in power_history[:5])}
{('...' if len(power_history) > 5 else '')}

【评估要求】
请根据以上信息，评估该国家的战略目标达成情况，并返回JSON格式的评估结果。"""

        return prompt

    def _get_evaluation_system_prompt(self) -> str:
        """获取评估系统提示词"""
        return """你是一个国际关系和战略评估专家，擅长运用克莱因国力方程和国际关系理论分析国家行为。

你的任务是评估一个国家在最近10轮仿真中的战略目标达成情况。

【评估维度说明】
1. 国力增长贡献度 (0-100): 评估国力变化是否符合该国实力层级和战略目标
   - 对于超级大国和大国：期望正向增长
   - 对于小国：至少保持稳定
   - 结合初始国力和当前国力变化幅度评分

2. 行为有效性 (0-100): 评估行为选择是否有助于实现国家利益偏好
   - 分析行为类别与国家利益偏好的匹配度
   - 考虑尊重主权行为占比（较高通常意味着更有效的策略）
   - 评估行为的一致性和连贯性

3. 领导类型一致性 (0-100): 评估行为是否符合该国领导类型的行为模式
   - 王道型：应更倾向于尊重主权、合作行为
   - 霸权型：可能采用双重标准，强调自身利益
   - 强权型：倾向使用强制手段
   - 昏庸型：行为可能缺乏一致性

4. 综合目标达成度 (0-100): 综合以上维度的加权评分
   - 权重建议：国力增长 30% + 行为有效性 40% + 领导一致性 30%

【输出要求】
请返回严格的JSON格式，包含以下字段：
{
    "goal_achievement_score": float (0-100),
    "power_growth_contribution": float (0-100),
    "action_effectiveness": float (0-100),
    "leadership_alignment": float (0-100),
    "overall_assessment": "综合评估说明（2-3句话）",
    "specific_achievements": "具体成就列表（分点列举）",
    "challenges": "面临的挑战和问题（分点列举）"
}

注意：overall_assessment、specific_achievements 和 challenges 字段使用中文，可以包含换行符。
"""

    async def _save_evaluation_result(
        self,
        project_id: int,
        agent_id: int,
        evaluation_round: int,
        start_round: int,
        end_round: int,
        evaluation_result: dict
    ) -> None:
        """保存评估结果到数据库"""
        async for session in db_config.get_session():
            evaluation = StrategicGoalEvaluation(
                project_id=project_id,
                agent_id=agent_id,
                evaluation_round=evaluation_round,
                evaluation_round_round_start=start_round,
                evaluation_round_end=end_round,
                goal_achievement_score=evaluation_result.get("goal_achievement_score", 0),
                power_growth_contribution=evaluation_result.get("power_growth_contribution"),
                action_effectiveness=evaluation_result.get("action_effectiveness"),
                leadership_alignment=evaluation_result.get("leadership_alignment"),
                overall_assessment=evaluation_result.get("overall_assessment"),
                specific_achievements=evaluation_result.get("specific_achievements"),
                challenges=evaluation_result.get("challenges"),
            )
            session.add(evaluation)

    async def evaluate_all_agents(self, project_id: int, evaluation_round: int) -> List[dict]:
        """评估项目中所有国家"""
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = result.scalars().all()

        results = []
        for agent in agents:
            result = await self.evaluate_agent_goal_achievement(
                project_id, agent.agent_id, evaluation_round
            )
            results.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                **result
            })

        logger.info(f"Evaluation completed for {len(results)} agents at round {evaluation_round}")
        return results


# Global instance
_goal_evaluation_service: Optional[GoalEvaluationService] = None


def get_goal_evaluation_service() -> GoalEvaluationService:
    """获取或创建全局评估服务实例"""
    global _goal_evaluation_service

    if _goal_evaluation_service is None:
        _goal_evaluation_service = GoalEvaluationService()

    return _goal_evaluation_service
