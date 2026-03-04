"""
代理管理路由模块

本模块提供代理（Agent）的CRUD操作端点：
- 列出所有代理
- 创建新代理
- 更新现有代理
- 删除代理
- 加载预设代理配置

核心端点：
- GET /: 列出所有代理摘要
- GET /{agent_id}: 获取指定代理的详细信息
- POST /: 创建新代理
- PUT /{agent_id}: 更新指定代理
- DELETE /{agent_id}: 删除指定代理
- POST /presets/{preset_name}: 加载预设代理配置
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, HTTPException, status

from api.models.schemas import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentSummaryResponse,
    AgentDetailResponse,
)


logger = logging.getLogger(__name__)
router = APIRouter()

# Global reference to simulation controller
simulation_controller = None


def set_controller(controller):
    """Set simulation controller reference."""
    global simulation_controller
    simulation_controller = controller


def _convert_agent_to_summary(agent) -> Dict:
    """
    Convert agent object to summary dictionary.

    Args:
        agent: Agent instance.

    Returns:
        Agent summary dictionary.
    """
    summary = agent.get_summary()
    return {
        "agent_id": summary.get("agent_id"),
        "name": summary.get("name"),
        "name_zh": summary.get("name_zh"),
        "agent_type": summary.get("agent_type"),
        "leadership_type": summary.get("leadership_type"),
        "leadership_name": summary.get("leadership_name"),
        "capability_tier": summary.get("capability_tier"),
        "capability_index": summary.get("capability_index"),
        "is_active": agent.is_active,
        "is_alive": agent.is_alive,
        "history_length": summary.get("history_length", 0),
        "relations_count": summary.get("relations_count", 0),
    }


def _convert_agent_to_detail(agent) -> Dict:
    """
    Convert agent object to detail dictionary.

    Args:
        agent: Agent instance.

    Returns:
        Agent detail dictionary.
    """
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "name_zh": agent.name_zh,
        "agent_type": agent.agent_type.value,
        "leadership_type": agent.leadership_type.value,
        "leadership_name": agent.leadership_profile.name if agent.leadership_profile else None,
        "is_active": agent.is_active,
        "is_alive": agent.is_alive,
        "capability_metrics": None,  # Will be populated from metrics
        "moral_metrics": None,
        "success_metrics": None,
        "relations": agent.relations,
    }


@router.get("/", response_model=List[AgentSummaryResponse], status_code=status.HTTP_200_OK)
async def list_agents() -> List[AgentSummaryResponse]:
    """
    List all agents in the simulation.

    Returns:
        List of agent summaries.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    agents = []
    for agent_id, agent in simulation_controller._agents.items():
        agents.append(_convert_agent_to_summary(agent))

    return agents


@router.get("/{agent_id}", response_model=AgentDetailResponse, status_code=status.HTTP_200_OK)
async def get_agent(agent_id: str) -> AgentDetailResponse:
    """
    Get detailed information about a specific agent.

    Args:
        agent_id: Agent identifier.

    Returns:
        Agent details.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    if agent_id not in simulation_controller._agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    agent = simulation_controller._agents[agent_id]
    return _convert_agent_to_detail(agent)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_agent(request: AgentCreateRequest):
    """
    Create a new agent.

    Args:
        request: Agent creation request.

    Returns:
        Created agent summary.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    # Check if agent ID already exists
    if request.agent_id in simulation_controller._agents:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent already exists: {request.agent_id}",
        )

    # Import models
    from src.models.agent import AgentType, Agent
    from src.models.leadership_type import LeadershipType
    from src.models.capability import Capability, HardPower, SoftPower

    # Convert request enums to Python enums
    try:
        agent_type = AgentType(request.agent_type.value)
        leadership_type = LeadershipType(request.leadership_type.value)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid enum value: {e}",
        )

    # Create capability
    capability = None
    if request.capability:
        hard_power = HardPower(
            military_capability=request.capability.hard_power.military_capability,
            nuclear_capability=request.capability.hard_power.nuclear_capability,
            conventional_forces=request.capability.hard_power.conventional_forces,
            force_projection=request.capability.hard_power.force_projection,
            gdp_share=request.capability.hard_power.gdp_share,
            economic_growth=request.capability.hard_power.economic_growth,
            trade_volume=request.capability.hard_power.trade_volume,
            financial_influence=request.capability.hard_power.financial_influence,
            technology_level=request.capability.hard_power.technology_level,
            military_technology=request.capability.hard_power.military_technology,
            innovation_capacity=request.capability.hard_power.innovation_capacity,
            energy_access=request.capability.hard_power.energy_access,
            strategic_materials=request.capability.hard_power.strategic_materials,
        )
        soft_power = SoftPower(
            discourse_power=request.capability.soft_power.discourse_power,
            narrative_control=request.capability.soft_power.narrative_control,
            media_influence=request.capability.soft_power.media_influence,
            allies_count=request.capability.soft_power.allies_count,
            ally_strength=request.capability.soft_power.ally_strength,
            network_position=request.capability.soft_power.network_position,
            diplomatic_support=request.capability.soft_power.diplomatic_support,
            moral_legitimacy=request.capability.soft_power.moral_legitimacy,
            cultural_influence=request.capability.soft_power.cultural_influence,
            un_influence=request.capability.soft_power.un_influence,
            institutional_leadership=request.capability.soft_power.institutional_leadership,
        )
        capability = Capability(
            agent_id=request.agent_id,
            hard_power=hard_power,
            soft_power=soft_power,
        )

    # Create agent based on type
    agent = None
    if agent_type == AgentType.GREAT_POWER:
        from src.models.agent import GreatPower
        agent = GreatPower(
            agent_id=request.agent_id,
            name=request.name,
            name_zh=request.name_zh,
            leadership_type=leadership_type,
            capability=capability,
        )
    elif agent_type == AgentType.SMALL_STATE:
        from src.models.agent import SmallState
        agent = SmallState(
            agent_id=request.agent_id,
            name=request.name,
            name_zh=request.name_zh,
            leadership_type=leadership_type,
            capability=capability,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported agent type: {agent_type}",
        )

    agent.is_active = request.is_active

    # Add to simulation controller
    simulation_controller._agents[request.agent_id] = agent

    logger.info(f"Created agent: {request.agent_id} ({request.name})")

    # Reinitialize controller if it was already initialized
    if simulation_controller.get_status().value != "not_initialized":
        simulation_controller.initialize()

    return _convert_agent_to_summary(agent)


@router.put("/{agent_id}", status_code=status.HTTP_200_OK)
async def update_agent(agent_id: str, request: AgentUpdateRequest):
    """
    Update an existing agent.

    Args:
        agent_id: Agent identifier.
        request: Agent update request.

    Returns:
        Updated agent summary.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    if agent_id not in simulation_controller._agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    agent = simulation_controller._agents[agent_id]

    # Update fields
    if request.name is not None:
        agent.name = request.name
    if request.name_zh is not None:
        agent.name_zh = request.name_zh
    if request.is_active is not None:
        agent.is_active = request.is_active

    # Update leadership type if specified
    if request.leadership_type is not None:
        from src.models.leadership_type import LeadershipType
        try:
            agent.leadership_type = LeadershipType(request.leadership_type.value)
            # Refresh leadership profile
            from src.models.leadership_type import get_leadership_profile
            agent.leadership_profile = get_leadership_profile(agent.leadership_type)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid leadership type: {e}",
            )

    # Update capability if specified
    if request.capability is not None:
        from src.models.capability import HardPower, SoftPower, Capability

        hard_power = HardPower(
            military_capability=request.capability.hard_power.military_capability,
            nuclear_capability=request.capability.hard_power.nuclear_capability,
            conventional_forces=request.capability.hard_power.conventional_forces,
            force_projection=request.capability.hard_power.force_projection,
            gdp_share=request.capability.hard_power.gdp_share,
            economic_growth=request.capability.hard_power.economic_growth,
            trade_volume=request.capability.hard_power.trade_volume,
            financial_influence=request.capability.hard_power.financial_influence,
            technology_level=request.capability.hard_power.technology_level,
            military_technology=request.capability.hard_power.military_technology,
            innovation_capacity=request.capability.hard_power.innovation_capacity,
                       energy_access=request.capability.hard_power.energy_access,
            strategic_materials=request.capability.hard_power.strategic_materials,
        )
        soft_power = SoftPower(
            discourse_power=request.capability.soft_power.discourse_power,
            narrative_control=request.capability.soft_power.narrative_control,
            media_influence=request.capability.soft_power.media_influence,
            allies_count=request.capability.soft_power.allies_count,
            ally_strength=request.capability.soft_power.ally_strength,
            network_position=request.capability.soft_power.network_position,
            diplomatic_support=request.capability.soft_power.diplomatic_support,
            moral_legitimacy=request.capability.soft_power.moral_legitimacy,
            cultural_influence=request.capability.soft_power.cultural_influence,
            un_influence=request.capability.soft_power.un_influence,
            institutional_leadership=request.capability.soft_power.institutional_leadership,
        )
        agent.capability = Capability(
            agent_id=agent_id,
            hard_power=hard_power,
            soft_power=soft_power,
        )

    logger.info(f"Updated agent: {agent_id}")

    return _convert_agent_to_summary(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_200_OK)
async def delete_agent(agent_id: str):
    """
    Delete an agent.

    Args:
        agent_id: Agent identifier.

    Returns:
        Deletion confirmation.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    if agent_id not in simulation_controller._agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    # Remove agent
    del simulation_controller._agents[agent_id]

    logger.info(f"Deleted agent: {agent_id}")

    return {"message": f"Agent deleted: {agent_id}"}


@router.post("/presets/{preset_name}", status_code=status.HTTP_201_CREATED)
async def load_preset_agents(preset_name: str):
    """
    Load a preset configuration of agents.

    Args:
        preset_name: Name of preset configuration.

    Returns:
        List of created agents.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    from src.models.agent import AgentType, GreatPower, SmallState
    from src.models.leadership_type import LeadershipType

    # Define presets
    presets = {
        "basic": [
            {
                "agent_id": "gp1",
                "name": "Country A",
                "name_zh": "国家A",
                "agent_type": AgentType.GREAT_POWER,
                "leadership_type": LeadershipType.WANGDAO,
            },
            {
                "agent_id": "gp2",
                "name": "Country B",
                "name_zh": "国家B",
                "agent_type": AgentType.GREAT_POWER,
                "leadership_type": LeadershipType.HEGEMON,
            },
            {
                "agent_id": "ss1",
                "name": "Small State C",
                "name_zh": "小国C",
                "agent_type": AgentType.SMALL_STATE,
                "leadership_type": LeadershipType.HUNYONG,
            },
        ],
    }

    if preset_name not in presets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset not found: {preset_name}",
        )

    created_agents = []
    for preset in presets[preset_name]:
        # Create agent
        if preset["agent_type"] == AgentType.GREAT_POWER:
            agent = GreatPower(
                agent_id=preset["agent_id"],
                name=preset["name"],
                name_zh=preset["name_zh"],
                leadership_type=preset["leadership_type"],
            )
        else:
            agent = SmallState(
                agent_id=preset["agent_id"],
                name=preset["name"],
                name_zh=preset["name_zh"],
                leadership_type=preset["leadership_type"],
            )

        simulation_controller._agents[preset["agent_id"]] = agent
        created_agents.append(_convert_agent_to_summary(agent))

    logger.info(f"Loaded preset agents: {preset_name}")

    return created_agents
