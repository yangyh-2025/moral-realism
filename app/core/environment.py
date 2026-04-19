"""
仿真环境模块
Simulation Environment Module

实现仿真环境初始化、信息池管理，支持预置场景和自定义初始化模式。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from loguru import logger

from .agent_base import AgentBase, RegionEnum, LeaderTypeEnum
from .klein_equation import PowerLevelEnum
from .action_manager import ActionConfig, get_all_actions, initialize_actions


class SimulationMode(str, Enum):
    """仿真模式枚举"""
    PRESET = "预置场景"
    CUSTOM = "自定义"


class SimulationStatus(str, Enum):
    """仿真状态枚举"""
    NOT_STARTED = "未启动"
    RUNNING = "运行中"
    PAUSED = "暂停"
    COMPLETED = "已完成"
    TERMINATED = "已终止"


class OrderType(str, Enum):
    """国际秩序类型枚举"""
    NORMATIVE_ACCEPTANCE = "规范接纳型"
    NON_INTERVENTION = "不干涉型"
    BIG_STICK_DETERRENCE = "大棒威慑型"
    TERROR_BALANCE = "恐怖平衡型"


class SimulationEnvironment:
    """
    仿真环境类

    负责仿真环境的初始化、信息池管理和状态控制。
    """

    def __init__(
        self,
        mode: SimulationMode = SimulationMode.CUSTOM,
        preset_scene_id: Optional[int] = None
    ):
        """
        初始化仿真环境

        Args:
            mode: 仿真模式（预置场景或自定义）
            preset_scene_id: 预置场景ID（预置场景模式必填）
        """
        self.mode = mode
        self.preset_scene_id = preset_scene_id

        # 仿真状态
        self.status = SimulationStatus.NOT_STARTED
        self.current_round = 0
        self.total_rounds = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # 信息池
        self.info_pool = {
            "agents": {},  # agent_id -> AgentBase
            "actions": {},  # action_id -> ActionConfig
            "history": [],  # 历史记录列表
            "power_history": {},  # agent_id -> list of power history
            "follower_relations": {},  # round_num -> follower relations
            "order_history": []  # order type history
        }

        # 初始化互动行为集
        initialize_actions()
        all_actions = get_all_actions()
        self.info_pool["actions"] = {action.action_id: action for action in all_actions}

    def initialize_from_preset(
        self,
        preset_scene_id: int,
        preset_config: Dict[str, Any]
    ) -> bool:
        """
        从预置场景初始化环境

        Args:
            preset_scene_id: 预置场景ID
            preset_config: 预置场景配置（包含智能体配置、仿真轮次等）

        Returns:
            初始化是否成功
        """
        try:
            self.mode = SimulationMode.PRESET
            self.preset_scene_id = preset_scene_id

            # 设置仿真轮次
            self.total_rounds = preset_config.get("total_rounds", 100)

            # 创建智能体
            agents_config = preset_config.get("agents", [])
            for agent_config in agents_config:
                agent = AgentBase(**agent_config)
                self.add_agent(agent)

            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"预置场景初始化失败: {str(e)}", exc_info=True)
            return False

    def initialize_custom(
        self,
        agents_config: List[Dict[str, Any]],
        total_rounds: int = 100
    ) -> bool:
        """
        自定义场景初始化环境

        Args:
            agents_config: 智能体配置列表
            total_rounds: 总仿真轮次

        Returns:
            初始化是否成功
        """
        try:
            self.mode = SimulationMode.CUSTOM
            self.preset_scene_id = None

            # 设置仿真轮次
            self.total_rounds = total_rounds

            # 创建智能体
            for agent_config in agents_config:
                agent = AgentBase(**agent_config)
                self.add_agent(agent)

            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"自定义场景初始化失败: {str(e)}", exc_info=True)
            return False

    def add_agent(self, agent: AgentBase) -> bool:
        """
        添加智能体到环境

        Args:
            agent: 智能体对象

        Returns:
            添加是否成功
        """
        try:
            agent_id = agent.agent_id

            # 验证agent_id唯一性
            if agent_id in self.info_pool["agents"]:
                raise ValueError(f"智能体ID {agent_id} 已存在")

            # 添加到信息池
            self.info_pool["agents"][agent_id] = agent

            # 初始化国力历史
            self.info_pool["power_history"][agent_id] = []

            # 记录初始国力
            self._record_power_history(
                agent_id=agent_id,
                round_num=0,
                start_power=agent.initial_total_power,
                end_power=agent.initial_total_power,
                change_value=0.0,
                change_rate=0.0
            )

            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"添加智能体失败: {str(e)}", exc_info=True)
            return False

    def remove_agent(self, agent_id: int) -> bool:
        """
        从环境中移除智能体

        Args:
            agent_id: 智能体ID

        Returns:
            移除是否成功
        """
        try:
            if agent_id not in self.info_pool["agents"]:
                raise ValueError(f"智能体ID {agent_id} 不存在")

            # 从信息池移除
            del self.info_pool["agents"][agent_id]
            del self.info_pool["power_history"][agent_id]

            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"移除智能体失败: {str(e)}", exc_info=True)
            return False

    def get_agent(self, agent_id: int) -> Optional[AgentBase]:
        """
        获取智能体

        Args:
            agent_id: 智能体ID

        Returns:
            智能体对象，不存在则返回None
        """
        return self.info_pool["agents"].get(agent_id)

    def get_all_agents(self) -> Dict[int, AgentBase]:
        """
        获取所有智能体

        Returns:
            智能体字典
        """
        return self.info_pool["agents"]

    def get_agents_by_power_level(
        self,
        power_level: PowerLevelEnum
    ) -> Dict[int, AgentBase]:
        """
        根据实力层级获取智能体

        Args:
            power_level: 实力层级

        Returns:
            符合条件的智能体字典
        """
        return {
            agent_id: agent
            for agent_id, agent in self.info_pool["agents"].items()
            if agent.power_level == power_level
        }

    def get_agents_by_region(
        self,
        region: RegionEnum
    ) -> Dict[int, AgentBase]:
        """
        根据区域获取智能体

        Args:
            region: 区域

        Returns:
            符合条件的智能体字典
        """
        return {
            agent_id: agent
            for agent_id, agent in self.info_pool["agents"].items()
            if agent.region == region
        }

    def get_action(self, action_id: int) -> Optional[ActionConfig]:
        """
        获取行为配置

        Args:
            action_id: 行为ID

        Returns:
            行为配置对象，不存在则返回None
        """
        return self.info_pool["actions"].get(action_id)

    def get_all_actions(self) -> Dict[int, ActionConfig]:
        """
        获取所有行为配置

        Returns:
            行为配置字典
        """
        return self.info_pool["actions"]

    def add_history_record(self, record: Dict[str, Any]) -> None:
        """
        添加历史记录

        Args:
            record: 历史记录字典
        """
        record["timestamp"] = datetime.now().isoformat()
        self.info_pool["history"].append(record)
        self.updated_at = datetime.now()

    def get_history(self, round_num: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取历史记录

        Args:
            round_num: 轮次序号（None表示获取全部）

        Returns:
            历史记录列表
        """
        if round_num is None:
            return self.info_pool["history"]

        return [
            record for record in self.info_pool["history"]
            if record.get("round_num") == round_num
        ]

    def _record_power_history(
        self,
        agent_id: int,
        round_num: int,
        start_power: float,
        end_power: float,
        change_value: float,
        change_rate: float
    ) -> None:
        """
        记录智能体国力历史

        Args:
            agent_id: 智能体ID
            round_num: 轮次序号
            start_power: 本轮初始国力
            end_power: 本轮结束国力
            change_value: 国力变化值
            change_rate: 国力增长率
        """
        history_entry = {
            "agent_id": agent_id,
            "round_num": round_num,
            "start_power": start_power,
            "end_power": end_power,
            "change_value": change_value,
            "change_rate": change_rate,
            "timestamp": datetime.now().isoformat()
        }

        self.info_pool["power_history"][agent_id].append(history_entry)
        self.updated_at = datetime.now()

    def get_power_history(
        self,
        agent_id: Optional[int] = None,
        round_num: Optional[int] = None
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        获取国力历史

        Args:
            agent_id: 智能体ID（None表示获取全部）
            round_num: 轮次序号（None表示获取全部）

        Returns:
            国力历史字典
        """
        if agent_id is None:
            # 返回所有智能体的国力历史
            if round_num is None:
                return self.info_pool["power_history"]
            else:
                return {
                    aid: [
                        entry for entry in history
                        if entry["round_num"] == round_num
                    ]
                    for aid, history in self.info_pool["power_history"].items()
                }
        else:
            # 返回指定智能体的国力历史
            if agent_id not in self.info_pool["power_history"]:
                return {}

            history = self.info_pool["power_history"][agent_id]

            if round_num is None:
                return {agent_id: history}
            else:
                return {
                    agent_id: [
                        entry for entry in history
                        if entry["round_num"] == round_num
                    ]
                }

    def set_follower_relations(
        self,
        round_num: int,
        relations: Dict[int, Optional[int]]
    ) -> None:
        """
        设置追随关系

        Args:
            round_num: 轮次序号
            relations: 追随关系字典（follower_id -> leader_id，None表示中立）
        """
        self.info_pool["follower_relations"][round_num] = {
            "round_num": round_num,
            "relations": relations,
            "timestamp": datetime.now().isoformat()
        }
        self.updated_at = datetime.now()

    def get_follower_relations(
        self,
        round_num: Optional[int] = None
    ) -> Dict[int, Optional[int]]:
        """
        获取追随关系

        Args:
            round_num: 轮次序号（None表示获取最新轮次）

        Returns:
            追随关系字典
        """
        if round_num is None:
            # 返回最新轮次的追随关系
            if not self.info_pool["follower_relations"]:
                return {}
            latest_round = max(self.info_pool["follower_relations"].keys())
            return self.info_pool["follower_relations"][latest_round]["relations"]
        else:
            # 返回指定轮次的追随关系
            if round_num not in self.info_pool["follower_relations"]:
                return {}
            return self.info_pool["follower_relations"][round_num]["relations"]

    def add_order_history(self, order_info: Dict[str, Any]) -> None:
        """
        添加秩序类型历史

        Args:
            order_info: 秩序信息字典
        """
        order_info["timestamp"] = datetime.now().isoformat()
        self.info_pool["order_history"].append(order_info)
        self.updated_at = datetime.now()

    def get_order_history(self, round_num: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取秩序类型历史

        Args:
            round_num: 轮次序号（None表示获取全部）

        Returns:
            秩序类型历史列表
        """
        if round_num is None:
            return self.info_pool["order_history"]

        return [
            order for order in self.info_pool["order_history"]
            if order.get("round_num") == round_num
        ]

    def start_simulation(self) -> bool:
        """
        启动仿真

        Returns:
            启动是否成功
        """
        try:
            if self.status != SimulationStatus.NOT_STARTED:
                raise ValueError(f"当前状态 {self.status.value} 不允许启动仿真")

            if not self.info_pool["agents"]:
                raise ValueError("环境中没有智能体，无法启动仿真")

            self.status = SimulationStatus.RUNNING
            self.current_round = 1
            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"启动仿真失败: {str(e)}", exc_info=True)
            return False

    def pause_simulation(self) -> bool:
        """
        暂停仿真

        Returns:
            暂停是否成功
        """
        try:
            if self.status != SimulationStatus.RUNNING:
                raise ValueError(f"当前状态 {self.status.value} 不允许暂停仿真")

            self.status = SimulationStatus.PAUSED
            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"暂停仿真失败: {str(e)}", exc_info=True)
            return False

    def resume_simulation(self) -> bool:
        """
        继续仿真

        Returns:
            继续是否成功
        """
        try:
            if self.status != SimulationStatus.PAUSED:
                raise ValueError(f"当前状态 {self.status.value} 不允许继续仿真")

            self.status = SimulationStatus.RUNNING
            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"继续仿真失败: {str(e)}", exc_info=True)
            return False

    def stop_simulation(self) -> bool:
        """
        终止仿真

        Returns:
            终止是否成功
        """
        try:
            if self.status not in [SimulationStatus.RUNNING, SimulationStatus.PAUSED]:
                raise ValueError(f"当前状态 {self.status.value} 不允许终止仿真")

            self.status = SimulationStatus.TERMINATED
            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"终止仿真失败: {str(e)}", exc_info=True)
            return False

    def complete_simulation(self) -> bool:
        """
        完成仿真

        Returns:
            完成是否成功
        """
        try:
            if self.status != SimulationStatus.RUNNING:
                raise ValueError(f"当前状态 {self.status.value} 不允许完成仿真")

            self.status = SimulationStatus.COMPLETED
            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"完成仿真失败: {str(e)}", exc_info=True)
            return False

    def reset_simulation(self) -> bool:
        """
        重置仿真到初始状态

        Returns:
            重置是否成功
        """
        try:
            self.status = SimulationStatus.NOT_STARTED
            self.current_round = 0

            # 重置所有智能体到初始状态
            for agent in self.info_pool["agents"].values():
                agent.reset_to_initial()

            # 清空历史记录
            self.info_pool["history"] = []
            self.info_pool["power_history"] = {
                agent_id: []
                for agent_id in self.info_pool["agents"].keys()
            }
            self.info_pool["follower_relations"] = {}
            self.info_pool["order_history"] = []

            # 重新记录初始国力
            for agent_id, agent in self.info_pool["agents"].items():
                self._record_power_history(
                    agent_id=agent_id,
                    round_num=0,
                    start_power=agent.initial_total_power,
                    end_power=agent.initial_total_power,
                    change_value=0.0,
                    change_rate=0.0
                )

            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"重置仿真失败: {str(e)}", exc_info=True)
            return False

    def advance_round(self) -> bool:
        """
        前进到下一轮

        Returns:
            前进是否成功
        """
        try:
            if self.status != SimulationStatus.RUNNING:
                raise ValueError(f"当前状态 {self.status.value} 不允许前进轮次")

            if self.current_round >= self.total_rounds:
                raise ValueError(f"已达到最大轮次 {self.total_rounds}，无法继续前进")

            self.current_round += 1
            self.updated_at = datetime.now()
            return True

        except Exception as e:
            logger.error(f"前进轮次失败: {str(e)}", exc_info=True)
            return False

    def get_environment_info(self) -> Dict[str, Any]:
        """
        获取环境信息

        Returns:
            环境信息字典
        """
        return {
            "mode": self.mode.value,
            "preset_scene_id": self.preset_scene_id,
            "status": self.status.value,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "agent_count": len(self.info_pool["agents"]),
            "action_count": len(self.info_pool["actions"]),
            "history_count": len(self.info_pool["history"]),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# 便捷函数
def create_environment(
    mode: SimulationMode = SimulationMode.CUSTOM,
    preset_scene_id: Optional[int] = None
) -> SimulationEnvironment:
    """
    创建仿真环境（便捷函数）

    Args:
        mode: 仿真模式
        preset_scene_id: 预置场景ID

    Returns:
        仿真环境对象
    """
    return SimulationEnvironment(mode=mode, preset_scene_id=preset_scene_id)
