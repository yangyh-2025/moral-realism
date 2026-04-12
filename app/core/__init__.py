"""
核心仿真引擎模块
Core Simulation Engine Module

包含CINC综合国力指数、智能体基类、互动行为集管理和仿真环境等核心组件。
"""

from .cinc_calculator import (
    PowerLevelEnum,
    CINCCalculator,
    calculate_cinc,
    determine_power_level,
    calculate_all_cincs,
    determine_all_power_levels,
    CINC_INDICATORS
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
    # CINC Calculator
    "PowerLevelEnum",
    "CINCCalculator",
    "calculate_cinc",
    "determine_power_level",
    "calculate_all_cincs",
    "determine_all_power_levels",
    "CINC_INDICATORS",

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
