"""
智能体工厂 - 根据实力层级创建对应的智能体实例

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Any, Optional

from domain.agents.base_agent import BaseAgent
from domain.agents.super_power import SuperPowerAgent
from domain.agents.great_power import GreatPowerAgent
from domain.agents.middle_power import MiddlePowerAgent
from domain.agents.small_power import SmallPowerAgent
from domain.power.power_metrics import PowerMetrics, PowerTier
from config.leader_types import LeaderType


class AgentFactory:
    """
    智能体工厂 - 根据实力层级创建对应的智能体

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    @staticmethod
    def create_agent(
        agent_id: str,
        name: str,
        region: str,
        power_metrics: PowerMetrics,
        power_tier: PowerTier,
        leader_type: Optional[LeaderType] = None
    ) -> BaseAgent:
        """
        创建智能体

        Args:
            agent_id: 智能体唯一ID
            name: 国家名称
            region: 国家所属区域
            power_metrics: 实力指标
            power_tier: 实力层级
            leader_type: 领导类型（仅超级大国和大国需要）

        Returns:
            智能体实例

        Raises:
            ValueError: 当参数配置不正确时
        """
        # 根据实力层级创建对应的智能体
        if power_tier == PowerTier.SUPERPOWER:
            agent = SuperPowerAgent(agent_id, name, region, power_metrics)

        elif power_tier == PowerTier.GREAT_POWER:
            agent = GreatPowerAgent(agent_id, name, region, power_metrics)

        elif power_tier == PowerTier.MIDDLE_POWER:
            agent = MiddlePowerAgent(agent_id, name, region, power_metrics)

        elif power_tier == PowerTier.SMALL_POWER:
            agent = SmallPowerAgent(agent_id, name, region, power_metrics)

        else:
            raise ValueError(f"未知的实力层级: {power_tier}")

        # 设置实力层级
        agent.power_tier = power_tier

        # 设置领导类型（如果需要）
        agent.set_leader_type(leader_type)

        # 完成初始化
        agent.complete_initialization()

        return agent

    @staticmethod
    def create_agent_uninitialized(
        agent_id: str,
        name: str,
        region: str,
        power_metrics: PowerMetrics,
        power_tier: PowerTier
    ) -> BaseAgent:
        """
        创建未初始化的智能体（不调用complete_initialization）

        用于批量创建时的两步初始化流程

        Args:
            agent_id: 智能体唯一ID
            name: 国家名称
            region: 国家所属区域
            power_metrics: 实力指标
            power_tier: 实力层级

        Returns:
            未完全初始化的智能体实例（需要调用set_leader_type和complete_initialization）
        """
        # 根据实力层级创建对应的智能体
        if power_tier == PowerTier.SUPERPOWER:
            agent = SuperPowerAgent(agent_id, name, region, power_metrics)

        elif power_tier == PowerTier.GREAT_POWER:
            agent = GreatPowerAgent(agent_id, name, region, power_metrics)

        elif power_tier == PowerTier.MIDDLE_POWER:
            agent = MiddlePowerAgent(agent_id, name, region, power_metrics)

        elif power_tier == PowerTier.SMALL_POWER:
            agent = SmallPowerAgent(agent_id, name, region, power_metrics)

        else:
            raise ValueError(f"未知的实力层级: {power_tier}")

        # 设置实力层级
        agent.power_tier = power_tier

        return agent

    @staticmethod
    def batch_create_agents(
        configs: list
    ) -> list:
        """
        批量创建智能体

        配置格式：
        {
            "agent_id": str,
            "name": str,
            "region": str,
            "power_metrics": PowerMetrics,
            "power_tier": PowerTier,
            "leader_type": Optional[LeaderType]
        }

        Args:
            configs: 智能体配置列表

        Returns:
            智能体实例列表
        """
        agents = []

        for config in configs:
            agent = AgentFactory.create_agent(
                agent_id=config["agent_id"],
                name=config["name"],
                region=config["region"],
                power_metrics=config["power_metrics"],
                power_tier=config["power_tier"],
                leader_type=config.get("leader_type")
            )
            agents.append(agent)

        return agents

    @staticmethod
    def get_agent_class(power_tier: PowerTier) -> type:
        """
        获取指定实力层级对应的智能体类

        Args:
            power_tier: 实力层级

        Returns:
            智能体类

        Raises:
            ValueError: 当实力层级未知时
        """
        agent_classes = {
            PowerTier.SUPERPOWER: SuperPowerAgent,
            PowerTier.GREAT_POWER: GreatPowerAgent,
            PowerTier.MIDDLE_POWER: MiddlePowerAgent,
            PowerTier.SMALL_POWER: SmallPowerAgent
        }

        if power_tier not in agent_classes:
            raise ValueError(f"未知的实力层级: {power_tier}")

        return agent_classes[power_tier]

    @staticmethod
    def validate_config(
        power_tier: PowerTier,
        leader_type: Optional[LeaderType] = None
    ) -> tuple[bool, Optional[str]]:
        """
        验证智能体配置是否正确

        Args:
            power_tier: 实力层级
            leader_type: 领导类型

        Returns:
            (是否有效, 错误信息)
        """
        if power_tier in [PowerTier.SUPERPOWER, PowerTier.GREAT_POWER]:
            if leader_type is None:
                return (
                    False,
                    f"{power_tier.value}必须配置领导类型（leader_type）"
                )
            return (True, None)

        elif power_tier in [PowerTier.MIDDLE_POWER, PowerTier.SMALL_POWER]:
            if leader_type is not None:
                return (
                    False,
                    f"{power_tier.value}不应配置领导类型（leader_type）"
                )
            return (True, None)

        else:
            return (False, f"未知的实力层级: {power_tier}")
