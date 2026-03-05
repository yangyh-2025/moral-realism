"""
道义现实主义ABM系统的控制代理实现

本模块实现ControllerAgent类，用于管理模拟工作流
并协调代理之间的互动。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType
from src.models.capability import Capability


logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """模拟参数配置类"""

    max_rounds: int = 100  # 最大回合数
    event_probability: float = 0.2  # 事件发生概率
    checkpoint_interval: int = 10  # 检查点保存间隔
    checkpoint_dir: str = "./data/checkpoints"  # 检查点目录
    log_level: str = "INFO"  # 日志级别


@dataclass
class ControllerState:
    """控制代理状态跟踪类"""

    current_round: int = 0  # 当前回合数
    is_running: bool = False  # 是否运行中
    is_paused: bool = False  # 是否已暂停
    total_decisions: int = 0  # 总决策数
    total_interactions: int = 0  # 总互动数
    event_count: int = 0  # 事件计数


@dataclass
class ControllerAgent(Agent):
    """
    控制代理类

    管理模拟工作流并协调代理互动的控制代理。
    """

    # 模拟配置
    config: SimulationConfig = field(default_factory=SimulationConfig)

    # 控制器状态跟踪
    state: ControllerState = field(default_factory=ControllerState)

    # 代理管理
    great_powers: Dict[str, Any] = field(default_factory=dict)  # 大国代理字典
    small_states: Dict[str, Any] = field(default_factory=dict)  # 小国代理字典
    organizations: Dict[str, Any] = field(default_factory=dict)  # 组织代理字典
    all_agents: Dict[str, Any] = field(default_factory=dict)  # 所有代理字典

    def __post_init__(self) -> None:
        """数据类初始化后的处理"""
        self.agent_type = AgentType.CONTROLLER

        if self.leadership_profile is None:
            from src.models.leadership_type import get_leadership_profile
            self.leadership_profile = get_leadership_profile(self.leadership_type)

        if self.capability is None:
            self.capability = Capability(agent_id=self.agent_id)

        self.relations[self.agent_id] = 1.0

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """做出模拟控制决策"""
        if context is None:
            context = {}

        action = situation.get("action", "continue")
        decision = {
            "agent_id": self.agent_id,
            "action": action,
            "rationale": f"控制器决策: {action}",
            "current_round": self.state.current_round,
            "is_running": self.state.is_running,
        }

        self.add_history("decision", f"决定执行 {action}", metadata={"decision": decision})
        return decision

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """响应模拟控制消息"""
        if context is None:
            context = {}

        message_type = message.get("type", "unknown")

        content = f"控制器确认收到来自 {sender_id} 的 {message_type}。"

        response = {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": content,
            "message_type": "acknowledgment",
            "current_round": self.state.current_round,
        }

        self.add_history("response", f"响应 {sender_id}", metadata={"response": response})
        return response

    def _create_agent(self, agent_config: Dict[str, Any]) -> None:
        """从配置创建代理实例"""
        agent_type = agent_config.get("agent_type")
        agent_id = agent_config.get("agent_id")

        if agent_type == "great_power":
            from src.agents.great_power_agent import GreatPowerAgent

            agent = GreatPowerAgent(
                agent_id=agent_id,
                name=agent_config.get("name", agent_id),
                name_zh=agent_config.get("name_zh", agent_id),
                leadership_type=LeadershipType(agent_config.get("leadership_type", "wangdao")),
            )
            self.great_powers[agent_id] = agent
            self.all_agents[agent_id] = agent

        elif agent_type == "small_state":
            from src.agents.small_state_agent import SmallStateAgent

            agent = SmallStateAgent(
                agent_id=agent_id,
                name=agent_config.get("name", agent_id),
                name_zh=agent_config.get("name_zh", agent_id),
                leadership_type=LeadershipType(agent_config.get("leadership_type", "hunyong")),
            )
            self.small_states[agent_id] = agent
            self.all_agents[agent_id] = agent

        elif agent_type == "organization":
            from src.agents.organization_agent import (
                OrganizationAgent,
                OrganizationType,
                DecisionRule,
            )

            org_type_str = agent_config.get("org_type", "global")
            org_type = OrganizationType(org_type_str)

            decision_rule_str = agent_config.get("decision_rule", "consensus")
            decision_rule = DecisionRule(decision_rule_str)

            agent = OrganizationAgent(
                agent_id=agent_id,
                name=agent_config.get("name", agent_id),
                name_zh=agent_config.get("name_zh", agent_id),
                leadership_type=LeadershipType(agent_config.get("leadership_type", "hegemon")),
                org_type=org_type,
                decision_rule=decision_rule,
            )
            self.organizations[agent_id] = agent
            self.all_agents[agent_id] = agent

    def start_simulation(self) -> None:
        """启动模拟"""
        self.state.is_running = True
        self.state.is_paused = False
        logger.info(f"模拟已启动，最大回合数: {self.config.max_rounds}")

    def pause_simulation(self) -> None:
        """暂停模拟"""
        self.state.is_paused = True
        logger.info("模拟已暂停")

    def resume_simulation(self) -> None:
        """恢复模拟"""
        self.state.is_paused = False
        logger.info("模拟已恢复")

    def stop_simulation(self) -> None:
        """停止模拟"""
        self.state.is_running = False
        self.state.is_paused = False
        logger.info("模拟已停止")

    def execute_round(self) -> None:
        """执行单个模拟回合"""
        if not self.state.is_running or self.state.is_paused:
            return

        # 增加回合数
        self.state.current_round += 1

        # 执行代理决策
        for agent_id, agent in self.all_agents.items():
            situation = {"round": self.state.current_round}
            available_actions = []
            context = {
                "agents": {aid: a.get_summary() for aid, a in self.all_agents.items()},
                "great_powers": {
                    aid: {"leadership_type": a.leadership_type.value, "name": a.name}
                    for aid, a in self.great_powers.items()
                },
            }

            decision = agent.decide(situation, available_actions, context)
            self.state.total_decisions += 1

        logger.info(f"第 {self.state.current_round} 回合已完成")

    def advance_round(self) -> None:
        """推进到下一回合"""
        self.state.current_round += 1
        logger.info(f"已推进到第 {self.state.current_round} 回合")

    def get_simulation_state(self) -> Dict[str, Any]:
        """获取完整的模拟状态摘要"""
        return {
            "current_round": self.state.current_round,
            "max_rounds": self.config.max_rounds,
            "is_running": self.state.is_running,
            "is_paused": self.state.is_paused,
            "great_power_count": len(self.great_powers),
            "small_state_count": len(self.small_states),
            "organization_count": len(self.organizations),
            "total_agents": len(self.all_agents),
            "total_decisions": self.state.total_decisions,
            "total_interactions": self.state.total_interactions,
            "event_count": self.state.event_count,
        }
