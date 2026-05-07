"""
战略关系演变服务 - RelationshipEvolutionService
使用LLM驱动的评估智能体，根据全局互动信息动态调整国家间的战略关系。

每轮仿真结束后调用，分析最近几轮的行为互动模式、国力变化、追随格局等，
逐对评估战略关系是否需要升级或降级。
"""

import json
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import db_config
from app.services.llm_service import get_llm_service
from app.models import (
    AgentConfig,
    ActionRecord,
    AgentPowerHistory,
    FollowerRelation,
    SimulationRound,
    StrategicRelationship,
)
from app.models.strategic_relationship import StrategicRelationshipEnum
from app.services.strategic_relationship_service import StrategicRelationshipService
from loguru import logger


# 关系等级排序（从敌对到友好）
RELATIONSHIP_LEVELS = [
    StrategicRelationshipEnum.WAR.value,
    StrategicRelationshipEnum.CONFLICT.value,
    StrategicRelationshipEnum.NO_DIPLOMACY.value,
    StrategicRelationshipEnum.PARTNERSHIP.value,
    StrategicRelationshipEnum.ALLIANCE.value,
]


class RelationshipEvolutionService:
    """
    战略关系演变服务 - LLM驱动的战略关系动态调整

    实现功能：
    - 收集全局信息（智能体状态、历史行为、国力变化、追随关系、秩序类型）
    - 构建LLM提示词，逐对评估战略关系
    - 解析LLM输出，更新数据库中的战略关系
    - 记录变化日志
    """

    def __init__(self, log_manager=None):
        self.llm_service = get_llm_service()
        self.log_manager = log_manager

    async def evolve_relationships(self, project_id: int, round_num: int) -> List[Dict[str, Any]]:
        """
        评估并演变项目中所有战略关系

        Args:
            project_id: 项目ID
            round_num: 当前轮次

        Returns:
            发生变化的关系列表
        """
        logger.info(f"开始第 {round_num} 轮战略关系演变评估")

        # 1. 收集全局信息
        agents = await self._get_agents(project_id)
        current_relationships = await self._get_current_relationships(project_id)
        recent_actions = await self._get_recent_actions(project_id, round_num, window=3)
        recent_power = await self._get_recent_power(project_id, round_num, window=3)
        recent_followers = await self._get_recent_followers(project_id, round_num)
        recent_order = await self._get_recent_order(project_id, round_num)

        if not current_relationships:
            logger.info(f"项目 {project_id} 没有战略关系，跳过演变")
            return []

        # 2. 构建LLM提示词
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            agents=agents,
            current_relationships=current_relationships,
            recent_actions=recent_actions,
            recent_power=recent_power,
            recent_followers=recent_followers,
            recent_order=recent_order,
            round_num=round_num,
        )

        # 3. 调用LLM
        try:
            response = await self.llm_service.call_llm_async(
                prompt=user_prompt,
                system_prompt=system_prompt,
                log_manager=self.log_manager,
                log_category="relationship_evolution",
                project_id=project_id,
                round_num=round_num,
            )
            logger.info(f"第 {round_num} 轮战略关系演变LLM响应完成")
        except Exception as e:
            logger.error(f"第 {round_num} 轮战略关系演变LLM调用失败: {e}", exc_info=True)
            return []

        # 4. 解析并应用变化
        changes = self._parse_changes(response, current_relationships)
        applied_changes = []

        for change in changes:
            if await self._apply_change(project_id, change):
                applied_changes.append(change)
                logger.info(
                    f"战略关系变化: {change['source_agent_id']} <-> {change['target_agent_id']} "
                    f"{change['current_type']} -> {change['new_type']}: {change['reason'][:50]}..."
                )
                # 记录日志
                if self.log_manager:
                    await self.log_manager.log_relationship_change(round_num, change)
            else:
                logger.warning(f"战略关系变化应用失败，跳过: {change}")

        logger.info(f"第 {round_num} 轮战略关系演变完成，{len(applied_changes)} 对关系发生变化")
        return applied_changes

    # ==================== 信息收集方法 ====================

    async def _get_agents(self, project_id: int) -> List[Dict[str, Any]]:
        """获取项目中的所有智能体信息"""
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = result.scalars().all()
            return [
                {
                    "agent_id": a.agent_id,
                    "agent_name": a.agent_name,
                    "region": a.region,
                    "power_level": a.power_level,
                    "leader_type": a.leader_type or "未定义",
                    "current_total_power": a.current_total_power,
                    "initial_total_power": a.initial_total_power,
                }
                for a in agents
            ]

    async def _get_current_relationships(self, project_id: int) -> List[Dict[str, Any]]:
        """获取当前所有战略关系"""
        async for session in db_config.get_session():
            result = await session.execute(
                select(StrategicRelationship).where(StrategicRelationship.project_id == project_id)
            )
            relations = result.scalars().all()
            return [
                {
                    "source_agent_id": r.source_agent_id,
                    "target_agent_id": r.target_agent_id,
                    "relationship_type": r.relationship_type,
                }
                for r in relations
            ]

    async def _get_recent_actions(
        self, project_id: int, round_num: int, window: int = 3
    ) -> List[Dict[str, Any]]:
        """获取最近N轮的行为记录"""
        start_round = max(1, round_num - window + 1)
        async for session in db_config.get_session():
            result = await session.execute(
                select(ActionRecord).where(
                    ActionRecord.project_id == project_id,
                    ActionRecord.round_num >= start_round,
                    ActionRecord.round_num <= round_num,
                )
            )
            records = result.scalars().all()
            return [
                {
                    "round_num": r.round_num,
                    "source_agent_id": r.source_agent_id,
                    "target_agent_id": r.target_agent_id,
                    "action_name": r.action_name,
                    "action_category": r.action_category,
                    "respect_sov": r.respect_sov,
                    "initiator_power_change": r.initiator_power_change,
                    "target_power_change": r.target_power_change,
                    "action_content": r.action_content or "",
                }
                for r in records
            ]

    async def _get_recent_power(
        self, project_id: int, round_num: int, window: int = 3
    ) -> List[Dict[str, Any]]:
        """获取最近N轮的国力历史"""
        start_round = max(1, round_num - window + 1)
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentPowerHistory).where(
                    AgentPowerHistory.project_id == project_id,
                    AgentPowerHistory.round_num >= start_round,
                    AgentPowerHistory.round_num <= round_num,
                )
            )
            records = result.scalars().all()
            return [
                {
                    "round_num": r.round_num,
                    "agent_id": r.agent_id,
                    "round_start_power": r.round_start_power,
                    "round_end_power": r.round_end_power,
                    "round_change_value": r.round_change_value,
                    "round_change_rate": r.round_change_rate,
                }
                for r in records
            ]

    async def _get_recent_followers(self, project_id: int, round_num: int) -> Dict[int, Optional[int]]:
        """获取最近一轮的追随关系"""
        async for session in db_config.get_session():
            result = await session.execute(
                select(FollowerRelation).where(
                    FollowerRelation.project_id == project_id,
                    FollowerRelation.round_num == round_num,
                )
            )
            records = result.scalars().all()
            return {r.follower_agent_id: r.leader_agent_id for r in records}

    async def _get_recent_order(self, project_id: int, round_num: int) -> Dict[str, Any]:
        """获取最近一轮的秩序信息"""
        async for session in db_config.get_session():
            result = await session.execute(
                select(SimulationRound).where(
                    SimulationRound.project_id == project_id,
                    SimulationRound.round_num == round_num,
                )
            )
            record = result.scalar_one_or_none()
            if record:
                return {
                    "order_type": record.order_type,
                    "has_leader": record.has_leader,
                    "leader_agent_id": record.leader_agent_id,
                    "leader_follower_ratio": record.leader_follower_ratio,
                    "respect_sov_ratio": record.respect_sov_ratio,
                }
            return {"order_type": "未确定", "has_leader": "false", "leader_agent_id": None}

    # ==================== 提示词构建 ====================

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一个国际关系与战略分析专家。你的任务是根据最近几轮的国际政治互动数据，评估每一对国家之间的战略关系是否需要调整。

【战略关系等级】（从敌对到友好）：
1. 战争关系 - 最高烈度敌对，处于武装冲突状态
2. 冲突关系 - 存在明显对抗和敌意，但未达到战争级别
3. 无外交关系 - 中立状态，无实质性互动或明确立场
4. 伙伴关系 - 存在合作倾向，有一定程度的互信
5. 盟友关系 - 最高级别友好关系，深度战略合作

【评估规则】：
1. 行为互动模式：分析两国之间最近的行为记录
   - 合作类行为（外交合作、经济援助、协商等）增多 → 关系倾向于升级（友好化）
   - 对抗类行为（威胁、制裁、军事展示、攻击等）增多 → 关系倾向于降级（敌对化）
2. 国力对比变化：如果一方国力显著增长并持续对另一方施压，关系可能恶化
3. 追随格局：如果两国追随同一领导者，关系倾向于改善；如果追随不同领导者，关系可能恶化
4. 第三方影响：盟友的行为可能影响关系（如盟友对某国敌对，本国关系也可能受影响）
5. 变化约束：
   - 每次变化最多只能升降一级（如从"无外交"只能到"冲突"或"伙伴"）
   - 如果近期两国之间没有显著互动，倾向于保持不变
   - 关系变化需要有明确的、基于数据的依据
6. 连续性：除非发生重大事件，否则关系不应频繁剧烈波动

【输出要求】：
- 必须输出严格的JSON格式
- 对每一对需要变化的关系给出明确的变化理由
- 如果没有明显变化依据，保持当前关系不变（不输出）
- 禁止使用markdown格式，禁止任何额外文本说明
"""

    def _build_user_prompt(
        self,
        agents: List[Dict],
        current_relationships: List[Dict],
        recent_actions: List[Dict],
        recent_power: List[Dict],
        recent_followers: Dict[int, Optional[int]],
        recent_order: Dict[str, Any],
        round_num: int,
    ) -> str:
        """构建用户提示词"""
        # 智能体信息
        agents_str = "\n".join(
            f"  ID:{a['agent_id']} 名称:{a['agent_name']} 区域:{a['region']} "
            f"层级:{a['power_level']} 领导类型:{a['leader_type']} CINC:{a['current_total_power']:.4f}"
            for a in agents
        )

        # 当前战略关系
        rel_str = "\n".join(
            f"  {r['source_agent_id']} <-> {r['target_agent_id']}: {r['relationship_type']}"
            for r in current_relationships
        )

        # 按关系对汇总行为记录
        pair_actions = defaultdict(list)
        for action in recent_actions:
            a, b = sorted([action["source_agent_id"], action["target_agent_id"]])
            pair_actions[(a, b)].append(action)

        pair_actions_str = ""
        for (a, b), actions in pair_actions.items():
            pair_actions_str += f"\n  关系对 {a} <-> {b}:\n"
            for act in actions:
                sov = "尊重主权" if act["respect_sov"] else "不尊重主权"
                pair_actions_str += (
                    f"    第{act['round_num']}轮: {act['source_agent_id']}->{act['target_agent_id']} "
                    f"{act['action_name']}({act['action_category']}) [{sov}]\n"
                )
        if not pair_actions_str:
            pair_actions_str = "  无"

        # CINC变化
        power_str = ""
        for agent in agents:
            agent_power = [p for p in recent_power if p["agent_id"] == agent["agent_id"]]
            if agent_power:
                lines = [
                    f"第{p['round_num']}轮: {p['round_start_power']:.6f}->{p['round_end_power']:.6f} "
                    f"(变化{p['round_change_value']:+.6f})"
                    for p in sorted(agent_power, key=lambda x: x["round_num"])
                ]
                power_str += f"  {agent['agent_id']}({agent['agent_name']}): {', '.join(lines)}\n"
        if not power_str:
            power_str = "  无"

        # 追随关系
        follower_str = "\n".join(
            f"  {fid}: 追随 {lid}" if lid else f"  {fid}: 中立"
            for fid, lid in recent_followers.items()
        ) or "  无"

        # 秩序信息
        order_str = (
            f"秩序类型: {recent_order['order_type']}, "
            f"有领导者: {recent_order['has_leader']}, "
            f"领导者ID: {recent_order['leader_agent_id']}, "
            f"尊重主权率: {recent_order.get('respect_sov_ratio', 0):.2%}"
        )

        return f"""【评估任务】
请基于以下全局信息，对每一对战略关系逐一评估是否需要调整。

【当前体系内所有国家】
{agents_str}

【当前战略关系】
{rel_str}

【最近3轮行为记录（按关系对分组）】
{pair_actions_str}

【最近CINC变化】
{power_str}

【追随关系】
{follower_str}

【当前秩序状态】
  {order_str}

【输出格式】
请输出JSON格式：
{{
  "relationship_changes": [
    {{
      "source_agent_id": <国家A ID>,
      "target_agent_id": <国家B ID>,
      "current_type": "当前关系类型",
      "new_type": "新关系类型",
      "reason": "详细的评估理由，基于数据说明为什么需要变化"
    }}
  ]
}}

注意：
1. 只有确实需要变化的关系才放入数组，没有变化则输出空数组
2. reason 必须引用具体的行为数据作为依据
3. 每次变化只能升降一级
"""

    # ==================== 结果解析与应用 ====================

    def _parse_changes(
        self, response: Any, current_relationships: List[Dict]
    ) -> List[Dict[str, Any]]:
        """解析LLM响应，提取关系变化"""
        changes = []

        if isinstance(response, dict):
            raw_changes = response.get("relationship_changes", [])
        elif isinstance(response, str):
            try:
                parsed = json.loads(response)
                raw_changes = parsed.get("relationship_changes", [])
            except json.JSONDecodeError:
                logger.warning(f"LLM响应不是有效JSON: {response[:200]}...")
                return []
        else:
            return []

        if not isinstance(raw_changes, list):
            logger.warning(f"relationship_changes 不是列表: {type(raw_changes)}")
            return []

        # 构建当前关系查找表
        rel_lookup = {}
        for r in current_relationships:
            a, b = sorted([r["source_agent_id"], r["target_agent_id"]])
            rel_lookup[(a, b)] = r["relationship_type"]

        for change in raw_changes:
            try:
                source_id = int(change.get("source_agent_id"))
                target_id = int(change.get("target_agent_id"))
                current_type = change.get("current_type", "").strip()
                new_type = change.get("new_type", "").strip()
                reason = change.get("reason", "").strip()

                if not new_type or not reason:
                    continue

                a, b = sorted([source_id, target_id])

                # 验证该关系对是否存在
                actual_current = rel_lookup.get((a, b))
                if actual_current is None:
                    logger.warning(f"关系对 {a}<->{b} 不存在，跳过")
                    continue

                # 如果current_type与实际情况不符，以实际为准
                if actual_current != current_type:
                    logger.debug(f"current_type 不匹配: 声明={current_type}, 实际={actual_current}")
                    current_type = actual_current

                # 如果新类型与当前类型相同，跳过
                if new_type == current_type:
                    continue

                # 验证变化是否只升降一级
                if not self._is_valid_level_change(current_type, new_type):
                    logger.warning(
                        f"变化超过一级: {current_type} -> {new_type}，跳过"
                    )
                    continue

                # 验证新类型是否有效
                if new_type not in RELATIONSHIP_LEVELS:
                    logger.warning(f"无效的关系类型: {new_type}，跳过")
                    continue

                changes.append({
                    "source_agent_id": a,
                    "target_agent_id": b,
                    "current_type": current_type,
                    "new_type": new_type,
                    "reason": reason,
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"解析变化项失败: {change}, 错误: {e}")
                continue

        return changes

    def _is_valid_level_change(self, current: str, new: str) -> bool:
        """检查变化是否只升降一级"""
        try:
            current_idx = RELATIONSHIP_LEVELS.index(current)
            new_idx = RELATIONSHIP_LEVELS.index(new)
            return abs(new_idx - current_idx) == 1
        except ValueError:
            return False

    async def _apply_change(self, project_id: int, change: Dict[str, Any]) -> bool:
        """将变化应用到数据库"""
        try:
            async for session in db_config.get_session():
                service = StrategicRelationshipService(session)
                await service.set_relationship(
                    project_id,
                    change["source_agent_id"],
                    change["target_agent_id"],
                    change["new_type"],
                )
                await session.commit()
                return True
        except Exception as e:
            logger.error(f"应用战略关系变化失败: {e}", exc_info=True)
            return False


# 全局单例
_relationship_evolution_service: Optional[RelationshipEvolutionService] = None


def get_relationship_evolution_service(log_manager=None) -> RelationshipEvolutionService:
    """获取或创建全局演变服务实例"""
    global _relationship_evolution_service
    if _relationship_evolution_service is None or log_manager is not None:
        _relationship_evolution_service = RelationshipEvolutionService(log_manager=log_manager)
    return _relationship_evolution_service
