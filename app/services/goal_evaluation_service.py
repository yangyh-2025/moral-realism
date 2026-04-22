"""
战略目标评估服务
使用LLM驱动的评估智能体，评估每个国家的战略目标达成度
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
    """
    战略目标评估服务 - LLM驱动的国家战略目标达成度评估

    使用大语言模型对国家在仿真中的战略目标达成情况进行多维度评估，
    包括国力增长贡献、行为有效性、领导类型一致性等。
    """

    def __init__(self, log_manager=None):
        """
        初始化战略目标评估服务

        Args:
            log_manager: 可选的日志管理器实例
        """
        # 复用现有的LLM服务，与其他智能体共享相同的LLM API
        self.llm_service = get_llm_service()
        self.log_manager = log_manager

    async def evaluate_agent_goal_achievement(
        self,
        project_id: int,
        agent_id: int,
        evaluation_round: int,
        evaluation_window: int = 10
    ) -> dict:
        """
        评估单个国家在最近N轮的战略目标达成度

        评估方法：
        1. 国力贡献度：使用Min-Max标准化计算（数据驱动）
        2. 行为有效性：使用LLM评估
        3. 综合目标达成度：两个维度的加权平均（各50%）

        Args:
            project_id: 项目ID
            agent_id: 智能体ID
            evaluation_round:当前轮次
            evaluation_window: 评估窗口（默认10轮）

        Returns:
            包含各维度评分和评估结果的字典
        """
        start_round = max(1, evaluation_round - evaluation_window + 1)

        logger.info(f"开始评估国家 {agent_id} 在第 {start_round}-{evaluation_round} 轮的战略目标达成度")

        # 1. 计算国力贡献度（数据驱动的Min-Max标准化）
        all_power_contribution = await self._calculate_power_growth_contribution(
            project_id, start_round, evaluation_round
        )
        power_contribution_score = all_power_contribution.get(agent_id, 50.0)

        # 2. 收集数据用于LLM评估行为有效性
        agent_info = await self._get_agent_info(project_id, agent_id)
        action_records = await self._get_action_records(project_id, agent_id, start_round, evaluation_round)
        power_history = await self._get_power_history(project_id, agent_id, start_round, evaluation_round)
        global_action_records = await self._get_global_action_records(project_id, start_round, evaluation_round)

        # 3. 构建评估提示词（仅用于行为有效性评估）
        prompt = self._build_evaluation_prompt(
            agent_info, action_records, power_history, global_action_records,
            start_round, evaluation_round, power_contribution_score
        )

        # 4. 调用LLM进行行为有效性评估
        try:
            llm_result = await self.llm_service.call_llm_async(
                prompt=prompt,
                system_prompt=self._get_evaluation_system_prompt(),
                log_manager=self.log_manager,
                log_category="goal_evaluation",
                project_id=project_id,
                agent_id=agent_id,
                agent_name=agent_info.get("agent_name", f"Agent_{agent_id}") if agent_info else f"Agent_{agent_id}",
                evaluation_round=evaluation_round,
                start_round=start_round,
                end_round=evaluation_round
            )
            logger.info(f"国家 {agent_id} 在第 {evaluation_round} 轮的LLM评估完成")
        except Exception as e:
            logger.error(f"国家 {agent_id} LLM评估失败: {e}")
            llm_result = {
                "action_effectiveness": 50.0,
                "overall_assessment": f"评估失败: {str(e)}",
                "specific_achievements": "无",
                "challenges": "评估服务异常"
            }

        action_effectiveness_score = llm_result.get("action_effectiveness", 50.0)

        # 5. 计算综合目标达成度（加权平均：国力贡献度50% + 行为有效性50%）
        goal_achievement_score = power_contribution_score * 0.5 + action_effectiveness_score * 0.5

        # 6. 构建最终评估结果
        evaluation_result = {
            "goal_achievement_score": round(goal_achievement_score, 2),
            "power_growth_contribution": power_contribution_score,
            "action_effectiveness": action_effectiveness_score,
            "leadership_alignment": None,
            "overall_assessment": llm_result.get("overall_assessment", ""),
            "specific_achievements": llm_result.get("specific_achievements", ""),
            "challenges": llm_result.get("challenges", "")
        }

        # 7. 保存评估结果
        await self._save_evaluation_result(
            project_id, agent_id, evaluation_round, start_round, evaluation_round, evaluation_result
        )

        return evaluation_result

    async def _get_agent_info(self, project_id: int, agent_id: int) -> Optional[dict]:
        """
        获取智能体的基本信息和国家利益偏好

        从数据库中获取智能体配置，并计算其国家利益偏好。

        Args:
            project_id: 项目ID
            agent_id: 智能体ID

        Returns:
            包含智能体信息和国家利益偏好的字典
        """
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
        """
        获取行为记录

        从数据库中获取指定轮次范围内的行为记录。

        Args:
            project_id: 项目ID
            agent_id: 智能体ID
            start_round: 起始轮次
            end_round: 结束轮次

        Returns:
            行为记录列表
        """
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
        """
        获取国力历史

        从数据库中获取指定轮次范围内的国力变化历史。

        Args:
            project_id: 项目ID
            agent_id: 智能体ID
            start_round: 起始轮次
            end_round: 结束轮次

        Returns:
            国力历史记录列表
        """
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

    async def _calculate_power_growth_contribution(
        self, project_id: int, start_round: int, end_round: int
    ) -> dict:
        """
        计算国力贡献度（数据驱动的Min-Max标准化）

        计算评估窗口内所有国家的平均国力增长值，
        然后使用Min-Max标准化方法将值映射到0-100范围。

        Args:
            project_id: 项目ID
            start_round: 起始轮次
            end_round: 结束轮次

        Returns:
            字典，键为agent_id，值为标准化后的国力贡献度（0-100）
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentPowerHistory).where(
                    AgentPowerHistory.project_id == project_id,
                    AgentPowerHistory.round_num >= start_round,
                    AgentPowerHistory.round_num <= end_round
                )
            )
            all_records = result.scalars().all()

        if not all_records:
            return {}

        # 按智能体分组计算平均国力增长
        agent_growth = {}
        for record in all_records:
            if record.agent_id not in agent_growth:
                agent_growth[record.agent_id] = []
            agent_growth[record.agent_id].append(record.round_change_value)

        agent_avg_growth = {
            agent_id: sum(changes) / len(changes) if changes else 0
            for agent_id, changes in agent_growth.items()
        }

        # Min-Max标准化： (value - min) / (max - min) * 100
        values = list(agent_avg_growth.values())
        if not values or len(set(values)) == 1:
            return {agent_id: 50.0 for agent_id in agent_avg_growth}

        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val

        if range_val == 0:
            return {agent_id: 50.0 for agent_id in agent_avg_growth}

        contribution_scores = {}
        for agent_id, avg_growth in agent_avg_growth.items():
            normalized = (avg_growth - min_val) / range_val * 100
            contribution_scores[agent_id] = round(normalized, 2)

        return contribution_scores

    async def _get_global_action_records(
        self, project_id: int, start_round: int, end_round: int
    ) -> List[dict]:
        """
        获取全局行为记录（所有国家）

        从数据库中获取指定轮次范围内所有国家的行为记录。

        Args:
            project_id: 项目ID
            start_round: 起始轮次
            end_round: 结束轮次

        Returns:
            所有行为记录列表
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(ActionRecord).where(
                    ActionRecord.project_id == project_id,
                    ActionRecord.round_num >= start_round,
                    ActionRecord.round_num <= end_round
                )
            )
            records = result.scalars().all()

            return [
                {
                    "round_num": r.round_num,
                    "source_agent_id": r.source_agent_id,
                    "action_name": r.action_name,
                    "action_category": r.action_category,
                    "respect_sov": r.respect_sov,
                    "initiator_power_change": r.initiator_power_change,
                    "target_power_change": r.target_power_change,
                }
                for r in records
            ]

    def _build_evaluation_prompt(
        self, agent_info, action_records, power_history, global_action_records,
        start_round, end_round, power_contribution_score
    ) -> str:
        """
        构建评估提示词（仅用于行为有效性评估）

        Args:
            agent_info: 智能体信息
            action_records: 该智能体的行为记录
            power_history: 国力历史
            global_action_records: 所有国家的行为记录
            start_round: 起始轮次
            end_round: 结束轮次
            power_contribution_score: 已计算的国力贡献度得分

        Returns:
            完整的评估提示词字符串
        """
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

        # 全局行为统计
        global_total_actions = len(global_action_records)
        global_respect_sov_count = sum(1 for r in global_action_records if r["respect_sov"])
        global_respect_sov_ratio = global_respect_sov_count / global_total_actions if global_total_actions > 0 else 0

        # 按智能体统计全局行为
        global_agent_actions = Counter(r["source_agent_id"] for r in global_action_records)
        agent_id = agent_info["agent_id"]
        agent_action_count = global_agent_actions.get(agent_id, 0)

        prompt = f"""请评估以下国家在最近{end_round - start_round + 1}轮仿真中的行为有效性。

【国家基本信息】
- 国家名称: {agent_info['agent_name']}
- 所属区域: {agent_info['region']}
- 实力层级: {agent_info['power_level']}
- 领导类型: {agent_info['leader_type']}
- 初始综合国力: {agent_info['initial_total_power']:.2f}
- 当前综合国力: {agent_info['current_total_power']:.2f}

【国家利益偏好】
{chr(10).join(f"- {interest}" for interest in agent_info['national_interest'])}

【已计算的国力贡献度得分】
- 国力贡献度: {power_contribution_score:.2f}/100 (基于Min-Max标准化)

【该国家行为统计（第{start_round}-{end_round}轮）】
- 总行为数: {total_actions}
- 尊重主权行为数: {respect_sov_count}
- 尊重主权率: {respect_sov_ratio:.2%}
- 国力总变化: {total_power_change:.2f}
- 平均轮次国力变化: {avg_power_change:.2f}

【行为类别分布】
{chr(10).join(f"- {cat}: {count}" for cat, count in action_categories.items())}

【全局行为统计（所有国家）】
- 全局总行为数: {global_total_actions}
- 该国家行为占比: {agent_action_count / global_total_actions * 100:.1f}%
- 全局尊重主权率: {global_respect_sov_ratio:.2%}

【国力变化详情】
{chr(10).join(f"第{r['round_num']}轮: {r['round_start_power']:.2f} → {r['round_end_power']:.2f} (变化: {r['round_change_value']:.2f}, 增长率: {r['round_change_rate']:.2%})" for r in power_history[:5])}
{('...' if len(power_history) > 5 else '')}

【评估要求】
请根据以上信息，评估该国家在这十轮中的执行行为是否达成了其预期的战略目的。
重点关注：
1. 行为选择与国家利益偏好的匹配度
2. 行为的一致性和连贯性
3. 行为是否有助于实现其战略目标

返回JSON格式的行为有效性评估结果。"""

        return prompt

    def _get_evaluation_system_prompt(self) -> str:
        """
        获取评估系统提示词

        定义LLM在评估过程中的角色和评估标准。
        注意：此提示词仅用于评估行为有效性维度。

        Returns:
            系统提示词字符串
        """
        return """你是一个国际关系和战略评估专家，擅长运用克莱因国力方程和国际关系理论分析国家行为。

你的任务是评估一个国家在最近10轮仿真中的行为有效性。

【评估维度说明】
行为有效性 (0-100): 评估行为选择是否有助于实现国家利益偏好
- 分析行为类别与国家利益偏好的匹配度
- 考虑行为的一致性和连贯性
- 观察并推测该国家在这十轮中的执行行为是否达成了其预期的战略目的
- 结合全局数据，评估该国行为在国际环境中的相对效果

注意：国力贡献度已经通过数据驱动的Min-Max标准化方法计算完成，
不需要你再次评估。你只需要评估行为有效性。

【输出要求】
请返回严格的JSON格式，包含以下字段：
{
    "action_effectiveness": float (0-100),
    "overall_assessment": "综合评估说明（2-3句话）",
    "specific_achievements": "具体成就列表（分点列举）",
    "challenges": "面临的挑战和问题（分点列举）"
}

注意：
1. action_effectiveness必须在0-100范围内
2. overall_assessment、specific_achievements 和 challenges 字段使用中文，可以包含换行符
3. 不要包含 goal_achievement_score、power_growth_contribution、leadership_alignment 字段
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
        """
        保存评估结果到数据库

        将评估结果保存到StrategicGoalEvaluation表中。

        Args:
            project_id: 项目ID
            agent_id: 智能体ID
            evaluation_round: 评估轮次
            start_round: 评估窗口起始轮次
            end_round: 评估窗口结束轮次
            evaluation_result: 评估结果字典
        """
        async for session in db_config.get_session():
            evaluation = StrategicGoalEvaluation(
                project_id=project_id,
                agent_id=agent_id,
                evaluation_round=evaluation_round,
                evaluation_round_start=start_round,
                evaluation_round_end=end_round,
                goal_achievement_score=evaluation_result.get("goal_achievement_score", 0),
                power_growth_contribution=evaluation_result.get("power_growth_contribution"),
                action_effectiveness=evaluation_result.get("action_effectiveness"),
                leadership_alignment=evaluation_result.get("leadership_alignment"),  # 新版本为None
                overall_assessment=evaluation_result.get("overall_assessment"),
                specific_achievements=evaluation_result.get("specific_achievements"),
                challenges=evaluation_result.get("challenges"),
            )
            session.add(evaluation)
            await session.commit()

        # 记录到日志文件
        if self.log_manager:
            await self.log_manager.log_goal_evaluation({
                "project_id": project_id,
                "agent_id": agent_id,
                "evaluation_round": evaluation_round,
                "start_round": start_round,
                "end_round": end_round,
                "goal_achievement_score": evaluation_result.get("goal_achievement_score"),
                "power_growth_contribution": evaluation_result.get("power_growth_contribution"),
                "action_effectiveness": evaluation_result.get("action_effectiveness"),
                "leadership_alignment": evaluation_result.get("leadership_alignment"),
                "overall_assessment": evaluation_result.get("overall_assessment"),
                "specific_achievements": evaluation_result.get("specific_achievements"),
                "challenges": evaluation_result.get("challenges"),
                "evaluation_notes": "国力贡献度由Min-Max标准化计算，行为有效性由LLM评估"
            })

    async def evaluate_all_agents(self, project_id: int, evaluation_round: int) -> List[dict]:
        """
        评估项目中所有国家的战略目标达成度

        遍历项目中的所有国家，逐个进行评估。

        Args:
            project_id: 项目ID
            evaluation_round: 评估轮次

        Returns:
            包含所有国家评估结果的列表
        """
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

        logger.info(f"在第 {evaluation_round} 轮完成了 {len(results)} 个国家的评估")
        return results


# 全局评估服务单例
_goal_evaluation_service: Optional[GoalEvaluationService] = None


def get_goal_evaluation_service(log_manager=None) -> GoalEvaluationService:
    """
    获取或创建全局评估服务实例

    使用单例模式确保整个应用共享同一个评估服务实例。

    Args:
        log_manager: 可选的日志管理器实例

    Returns:
        GoalEvaluationService单例实例
    """
    global _goal_evaluation_service

    if _goal_evaluation_service is None or log_manager is not None:
        _goal_evaluation_service = GoalEvaluationService(log_manager=log_manager)

    return _goal_evaluation_service
