"""
CINC国力更新引擎
CINC Power Update Engine

CINC国力更新引擎。行为影响底层6指标 → 全局重算CINC → 全局重算层级。

更新流程（每轮）：
1. 行为发生 → 根据power_change和行为类别，计算每个国家受影响的6项底层指标变化量
2. 更新底层指标 → 所有国家的6个指标值更新
3. 全局重算CINC → 基于所有国家的新指标总和，重新计算所有国家的CINC（被动变化）
4. 全局重算层级 → 按新的CINC排名，重新判定所有国家的层级

关键认知：CINC是比例值。当一个国家的底层指标变化时，全球指标总和变化，
所有国家的CINC都会被动变化。
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid

from .cinc_calculator import (
    CINCCalculator,
    PowerLevelEnum,
    CINC_INDICATORS,
)

logger = logging.getLogger(__name__)


# 行为类别 → 6项指标的影响权重映射
# power_change × scale_factor × category_weight = 该指标的实际变化量
ACTION_CATEGORY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "外交手段": {
        "milex": 0.0,
        "milper": 0.0,
        "irst": 0.2,
        "pec": 0.6,
        "tpop": 0.0,
        "upop": 0.2,
    },
    "经济手段": {
        "milex": 0.0,
        "milper": 0.0,
        "irst": 0.4,
        "pec": 0.4,
        "tpop": 0.0,
        "upop": 0.2,
    },
    "军事手段": {
        "milex": 0.5,
        "milper": 0.3,
        "irst": 0.0,
        "pec": 0.2,
        "tpop": 0.0,
        "upop": 0.0,
    },
    "信息手段": {
        "milex": 0.0,
        "milper": 0.0,
        "irst": 0.1,
        "pec": 0.5,
        "tpop": 0.0,
        "upop": 0.4,
    },
}

# 各指标的scale_factor：将-1到+1的power_change映射到合理的指标变化量
INDICATOR_SCALE_FACTORS: Dict[str, float] = {
    "milex": 10000.0,  # 万级
    "milper": 1000.0,  # 千级
    "irst": 5000.0,    # 万级
    "pec": 10000.0,    # 万级
    "tpop": 100000.0,  # 十万级
    "upop": 50000.0,   # 万级
}


@dataclass
class IndicatorChange:
    """指标变化明细"""
    milex_delta: float = 0.0
    milper_delta: float = 0.0
    irst_delta: float = 0.0
    pec_delta: float = 0.0
    tpop_delta: float = 0.0
    upop_delta: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "milex_delta": self.milex_delta,
            "milper_delta": self.milper_delta,
            "irst_delta": self.irst_delta,
            "pec_delta": self.pec_delta,
            "tpop_delta": self.tpop_delta,
            "upop_delta": self.upop_delta,
        }

    def add(self, other: "IndicatorChange") -> None:
        """累加另一个变化"""
        self.milex_delta += other.milex_delta
        self.milper_delta += other.milper_delta
        self.irst_delta += other.irst_delta
        self.pec_delta += other.pec_delta
        self.tpop_delta += other.tpop_delta
        self.upop_delta += other.upop_delta


@dataclass
class CINCUpdateResult:
    """单个国家CINC更新结果"""
    agent_id: int
    agent_name: str
    start_cinc: float  # 轮次开始时的CINC
    end_cinc: float  # 轮次结束时的CINC
    cinc_change: float  # CINC绝对变化量
    cinc_change_rate: float  # CINC变化率（百分比）
    old_power_level: PowerLevelEnum
    new_power_level: PowerLevelEnum
    indicator_changes: IndicatorChange
    passive_change: bool  # 是否仅因他国变化导致的被动变化
    action_count: int = 0


@dataclass
class PowerHistoryEntry:
    """国力历史记录条目（向后兼容PowerUpdateEngine接口）"""
    history_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[int] = None
    agent_id: int = 0
    round_id: Optional[int] = None
    round_num: int = 0
    round_start_power: float = 0.0  # 现在存CINC值
    round_end_power: float = 0.0
    round_change_value: float = 0.0
    round_change_rate: float = 0.0
    indicator_changes: Optional[Dict[str, float]] = None
    passive_change: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class CINCPowerUpdateError(Exception):
    """CINC国力更新错误"""
    pass


def calculate_indicator_changes(
    power_change: float,
    action_category: str,
    primary_indicator: Optional[str] = None,
    secondary_indicator: Optional[str] = None,
) -> IndicatorChange:
    """
    根据power_change和行为类别，计算6项底层指标的变化量

    Args:
        power_change: 行为对应的国力变化值（-1到+1）
        action_category: 行为类别（"外交手段"/"经济手段"/"军事手段"/"信息手段"）
        primary_indicator: 主要影响指标（可选，覆盖类别默认）
        secondary_indicator: 次要影响指标（可选，覆盖类别默认）

    Returns:
        IndicatorChange，包含6项指标的变化量
    """
    weights = ACTION_CATEGORY_WEIGHTS.get(action_category)
    if weights is None:
        # 未知类别，默认使用外交权重
        weights = ACTION_CATEGORY_WEIGHTS["外交手段"]

    # 如果指定了 primary/secondary indicator，覆盖默认权重
    if primary_indicator and primary_indicator in CINC_INDICATORS:
        weights = {ind: 0.0 for ind in CINC_INDICATORS}
        weights[primary_indicator] = 0.7
        if secondary_indicator and secondary_indicator in CINC_INDICATORS:
            weights[secondary_indicator] = 0.3

    change = IndicatorChange()
    for ind in CINC_INDICATORS:
        weight = weights.get(ind, 0.0)
        scale = INDICATOR_SCALE_FACTORS.get(ind, 1.0)
        delta = power_change * scale * weight
        setattr(change, f"{ind}_delta", delta)

    return change


class CINCPowerUpdateEngine:
    """
    CINC国力更新引擎

    替代旧版PowerUpdateEngine，支持CINC比例值的被动变化机制。
    维护每个智能体的6项底层指标，行为影响指标→重算CINC→重算层级。
    """

    def __init__(
        self,
        max_action_change: float = 1.0,
        enable_logging: bool = True,
    ):
        """
        Args:
            max_action_change: 单次行为power_change的硬约束（-1到+1）
            enable_logging: 是否启用日志
        """
        self.max_action_change = max_action_change
        self.enable_logging = enable_logging
        # 智能体状态：{agent_id: {6项指标 + cinc + power_level + name}}
        self._agents: Dict[int, Dict[str, Any]] = {}
        # 国力历史
        self._power_history: Dict[int, List[PowerHistoryEntry]] = {}
        self._current_round = 0

        logger.info(
            f"CINCPowerUpdateEngine initialized "
            f"(max_action_change={max_action_change})"
        )

    def load_agents(self, agents: List[Dict[str, Any]]) -> None:
        """
        加载智能体列表

        Args:
            agents: 智能体列表，每项必须包含
                agent_id, agent_name, milex, milper, irst, pec, tpop, upop, cinc, power_level
        """
        self._agents = {}
        for agent in agents:
            aid = agent.get("agent_id")
            if aid is None:
                continue
            self._agents[aid] = {
                "agent_id": aid,
                "agent_name": agent.get("agent_name", f"Agent_{aid}"),
                "milex": float(agent.get("milex", 0)),
                "milper": float(agent.get("milper", 0)),
                "irst": float(agent.get("irst", 0)),
                "pec": float(agent.get("pec", 0)),
                "tpop": float(agent.get("tpop", 0)),
                "upop": float(agent.get("upop", 0)),
                "cinc": float(agent.get("cinc", 0)),
                "power_level": agent.get("power_level", PowerLevelEnum.SMALL_STATE),
            }
            self._power_history.setdefault(aid, [])

        logger.info(f"Loaded {len(self._agents)} agents into CINC engine")

    def set_round(self, round_num: int) -> None:
        self._current_round = round_num

    def _aggregate_round_changes(
        self,
        action_records: List[Dict[str, Any]],
    ) -> Dict[int, Tuple[IndicatorChange, int]]:
        """
        聚合本轮所有行为对每个国家的指标变化

        Args:
            action_records: 行为记录列表

        Returns:
            字典 {agent_id: (累计指标变化, 涉及行为数)}
        """
        agent_changes: Dict[int, IndicatorChange] = {
            aid: IndicatorChange() for aid in self._agents
        }
        agent_action_count: Dict[int, int] = {aid: 0 for aid in self._agents}

        for rec in action_records:
            source_id = rec.get("source_agent_id")
            target_id = rec.get("target_agent_id")
            initiator_change = float(rec.get("initiator_power_change", 0) or 0)
            target_change = float(rec.get("target_power_change", 0) or 0)
            category = rec.get("action_category", "外交手段")
            primary = rec.get("primary_indicator")
            secondary = rec.get("secondary_indicator")

            # 校验power_change约束
            if abs(initiator_change) > self.max_action_change:
                logger.warning(
                    f"行为{rec.get('action_name')} initiator变化{initiator_change}超限"
                )
                initiator_change = max(-self.max_action_change,
                                       min(self.max_action_change, initiator_change))
            if abs(target_change) > self.max_action_change:
                logger.warning(
                    f"行为{rec.get('action_name')} target变化{target_change}超限"
                )
                target_change = max(-self.max_action_change,
                                    min(self.max_action_change, target_change))

            # 计算发起方的指标变化
            if source_id in agent_changes:
                init_delta = calculate_indicator_changes(
                    initiator_change, category, primary, secondary
                )
                agent_changes[source_id].add(init_delta)
                agent_action_count[source_id] += 1

            # 计算目标方的指标变化
            if target_id in agent_changes and target_id != source_id:
                target_delta = calculate_indicator_changes(
                    target_change, category, primary, secondary
                )
                agent_changes[target_id].add(target_delta)
                agent_action_count[target_id] += 1

        return {
            aid: (agent_changes[aid], agent_action_count[aid])
            for aid in self._agents
        }

    def update_round(
        self,
        action_records: List[Dict[str, Any]],
    ) -> List[CINCUpdateResult]:
        """
        基于本轮行为更新所有国家的CINC

        流程：
        1. 聚合本轮所有行为对每个国家的指标变化
        2. 应用指标变化到agent状态
        3. 全局重算CINC（所有国家被动变化）
        4. 全局重算层级
        5. 记录历史

        Args:
            action_records: 行为记录列表

        Returns:
            每个国家的更新结果
        """
        if self.enable_logging:
            logger.info(
                f"CINC更新: 第{self._current_round}轮, "
                f"{len(action_records)}条行为, {len(self._agents)}个国家"
            )

        # Step 1: 记录更新前的状态
        old_cincs: Dict[int, float] = {
            aid: agent["cinc"] for aid, agent in self._agents.items()
        }
        old_levels: Dict[int, PowerLevelEnum] = {
            aid: agent["power_level"] for aid, agent in self._agents.items()
        }

        # Step 2: 聚合并应用指标变化
        agent_changes = self._aggregate_round_changes(action_records)

        for aid, (change, _) in agent_changes.items():
            agent = self._agents[aid]
            for ind in CINC_INDICATORS:
                delta = getattr(change, f"{ind}_delta", 0.0)
                new_val = agent[ind] + delta
                # 确保指标不为负
                agent[ind] = max(0.0, new_val)

        # Step 3: 全局重算CINC
        agents_indicators = [
            {
                "agent_id": aid,
                **{ind: agent[ind] for ind in CINC_INDICATORS},
            }
            for aid, agent in self._agents.items()
        ]
        new_cincs = CINCCalculator.calculate_all_cincs(agents_indicators)

        # Step 4: 全局重算层级
        new_levels = CINCCalculator.determine_all_power_levels(new_cincs)

        # Step 5: 应用结果并记录
        results: List[CINCUpdateResult] = []
        for aid, agent in self._agents.items():
            old_cinc = old_cincs[aid]
            new_cinc = new_cincs.get(aid, 0.0)
            old_level = old_levels[aid]
            new_level = new_levels.get(aid, PowerLevelEnum.SMALL_STATE)
            change, action_count = agent_changes[aid]

            agent["cinc"] = new_cinc
            agent["power_level"] = new_level

            cinc_change = new_cinc - old_cinc
            change_rate = (cinc_change / old_cinc * 100.0) if old_cinc > 0 else 0.0
            passive = action_count == 0

            result = CINCUpdateResult(
                agent_id=aid,
                agent_name=agent["agent_name"],
                start_cinc=old_cinc,
                end_cinc=new_cinc,
                cinc_change=cinc_change,
                cinc_change_rate=change_rate,
                old_power_level=old_level,
                new_power_level=new_level,
                indicator_changes=change,
                passive_change=passive,
                action_count=action_count,
            )
            results.append(result)

            # 记录历史
            entry = PowerHistoryEntry(
                agent_id=aid,
                round_num=self._current_round,
                round_start_power=old_cinc,
                round_end_power=new_cinc,
                round_change_value=cinc_change,
                round_change_rate=change_rate,
                indicator_changes=change.to_dict(),
                passive_change=passive,
            )
            self._power_history[aid].append(entry)

            if self.enable_logging:
                logger.info(
                    f"国家{agent['agent_name']}(ID:{aid}): "
                    f"CINC {old_cinc:.6f} -> {new_cinc:.6f} "
                    f"(变化{cinc_change:+.6f}, {change_rate:+.2f}%), "
                    f"层级 {old_level.value if hasattr(old_level, 'value') else old_level} "
                    f"-> {new_level.value if hasattr(new_level, 'value') else new_level}, "
                    f"被动={passive}"
                )

        return results

    def get_agent_state(self, agent_id: int) -> Optional[Dict[str, Any]]:
        """获取指定智能体的当前状态"""
        return self._agents.get(agent_id)

    def get_all_states(self) -> Dict[int, Dict[str, Any]]:
        """获取所有智能体的当前状态"""
        return self._agents.copy()

    def get_agent_cinc(self, agent_id: int) -> Optional[float]:
        """获取智能体当前CINC"""
        agent = self._agents.get(agent_id)
        return agent["cinc"] if agent else None

    def get_agent_power_history(
        self, agent_id: int, round_range: Optional[Tuple[int, int]] = None
    ) -> List[PowerHistoryEntry]:
        """获取智能体国力历史"""
        history = self._power_history.get(agent_id, [])
        if round_range:
            start, end = round_range
            history = [h for h in history if start <= h.round_num <= end]
        return history

    def reset(self) -> None:
        """清空状态"""
        self._agents.clear()
        self._power_history.clear()
        self._current_round = 0


# ============================================================
# 向后兼容API（保持与旧PowerUpdateEngine接口相似）
# ============================================================

class PowerUpdateEngine(CINCPowerUpdateEngine):
    """旧接口的兼容类"""
    pass
