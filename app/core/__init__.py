"""
核心仿真引擎模块
Core Simulation Engine Module

包含克莱因国力方程、智能体基类、互动行为集管理和仿真环境等核心组件。
"""

from .klein_equation import (
    KleinEquation,
    PowerLevelEnum,
    calculate_klein_power,
    determine_power_level
)

from .agent_base import (
    AgentBase,
    RegionEnum,
    LeaderTypeEnum,
    ActionConfig
)

from .action_manager import (
    ActionConfig as ActionConfigFull,
    ActionCategoryEnum,
    get_all_actions,
    get_action_by_id,
    get_action_by_name,
    get_initiative_actions,
    get_response_actions,
    get_action_statistics
)

from .environment import (
    SimulationEnvironment,
    SimulationMode,
    SimulationStatus,
    OrderType,
    create_environment
)

__all__ = [
    # Klein Equation
    "KleinEquation",
    "PowerLevelEnum",
    "calculate_klein_power",
    "determine_power_level",

    # Agent Base
    "AgentBase",
    "RegionEnum",
    "LeaderTypeEnum",
    "ActionConfig",

    # Action Manager
    "ActionConfigFull",
    "ActionCategoryEnum",
    "get_all_actions",
    "get_action_by_id",
    "get_action_by_name",
    "get_initiative_actions",
    "get_response_actions",
    "get_action_statistics",

    # Environment

    "SimulationEnvironment",
    "SimulationMode",
    "SimulationStatus",
    "OrderType",
    "create_environment"
]
