"""
模拟控制路由模块

本模块提供模拟生命周期管理的API端点：
- 启动、暂停、恢复、停止、重置模拟
- 查询模拟状态
- 配置模拟参数

核心端点：
- POST /start: 启动模拟
- POST /pause: 暂停模拟
- POST /resume: 恢复模拟
- POST /stop: 停止模拟
- POST /reset: 重置模拟
- POST /configure: 配置模拟参数
- GET /status: 获取模拟状态
"""

import asyncio
import logging
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, status

from api.models.schemas import (
    SimulationConfigRequest,
    SimulationStatusResponse,
    ControllerStateResponse,
    ControllerStatsResponse,
)


logger = logging.getLogger(__name__)
router = APIRouter()

# Global reference to simulation controller and ws_manager
# These will be set by the main application
simulation_controller = None
ws_manager = None


def set_controller(controller):
    """Set the simulation controller reference."""
    global simulation_controller
    simulation_controller = controller


def set_ws_manager(manager):
    """Set the WebSocket manager reference."""
    global ws_manager
    ws_manager = manager


async def run_simulation_async():
    """
    Run simulation in async context.

    Executes rounds continuously and broadcasts updates via WebSocket.
    """
    if simulation_controller is None:
        logger.error("Simulation controller not initialized")
        return

    sim_id = "default"  # Default simulation ID

    try:
        while simulation_controller.is_running():
            # Check if paused
            if simulation_controller.is_paused():
                await asyncio.sleep(0.1)
                continue

            # Execute single round
            result = simulation_controller.execute_single_round()

            if result is None:
                # Simulation completed or error
                break

            # Broadcast round completion via WebSocket
            if ws_manager and ws_manager.has_subscribers(sim_id):
                await ws_manager.send_round_complete(
                    sim_id,
                    result.get("round", 0),
                    result,
                )
                await ws_manager.send_status_update(
                    sim_id,
                    simulation_controller.get_status().value,
                    simulation_controller.get_controller_summary(),
                )

            # Small delay to prevent tight loop
            await asyncio.sleep(0.01)

        # Simulation completed
        if ws_manager and ws_manager.has_subscribers(sim_id):
            summary = simulation_controller.get_controller_summary()
            await ws_manager.send_simulation_complete(sim_id, summary)

    except Exception as e:
        logger.error(f"Simulation execution error: {e}", exc_info=True)
        if ws_manager and ws_manager.has_subscribers(sim_id):
            await ws_manager.send_error(sim_id, str(e))


# Global simulation task
sim_task: Optional[asyncio.Task] = None


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_simulation():
    """
    Start simulation execution.

    Returns:
        Simulation status after starting.
    """
    global sim_task

    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    # Check if already running
    if simulation_controller.is_running():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation is already running",
        )

    # Start simulation
    if not simulation_controller.start():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to start simulation",
        )

    # Start async simulation task
    sim_task = asyncio.create_task(run_simulation_async())

    logger.info("Simulation started")

    # Broadcast status update
    if ws_manager:
        await ws_manager.send_status_update(
            "default",
            simulation_controller.get_status().value,
            simulation_controller.get_controller_summary(),
        )

    return get_status_response()


@router.post("/pause", status_code=status.HTTP_200_OK)
async def pause_simulation():
    """
    Pause simulation execution.

    Returns:
        Simulation status after pausing.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    if not simulation_controller.is_running():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation is not running",
        )

    if not simulation_controller.pause():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to pause simulation",
        )

    logger.info("Simulation paused")

    # Broadcast status update
    if ws_manager:
        await ws_manager.send_status_update(
            "default",
            simulation_controller.get_status().value,
            simulation_controller.get_controller_summary(),
        )

    return get_status_response()


@router.post("/resume", status_code=status.HTTP_200_OK)
async def resume_simulation():
    """
    Resume simulation execution.

    Returns:
        Simulation status after resuming.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    if not simulation_controller.is_paused():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation is not paused",
        )

    if not simulation_controller.resume():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to resume simulation",
        )

    logger.info("Simulation resumed")

    # Broadcast status update
    if ws_manager:
        await ws_manager.send_status_update(
            "default",
            simulation_controller.get_status().value,
            simulation_controller.get_controller_summary(),
        )

    return get_status_response()


@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_simulation():
    """
    Stop simulation execution.

    Returns:
        Simulation status after stopping.
    """
    global sim_task

    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    if not simulation_controller.is_running() and not simulation_controller.is_paused():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation is not running or paused",
        )

    if not simulation_controller.stop():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to stop simulation",
        )

    # Cancel simulation task
    if sim_task and not sim_task.done():
        sim_task.cancel()
        try:
            await sim_task
        except asyncio.CancelledError:
            pass

    logger.info("Simulation stopped")

    # Broadcast status update
    if ws_manager:
        await ws_manager.send_status_update(
            "default",
            simulation_controller.get_status().value,
            simulation_controller.get_controller_summary(),
        )

    return get_status_response()


@router.post("/reset", status_code=status.HTTP_200_OK)
async def reset_simulation():
    """
    Reset simulation state.

    Returns:
        Simulation status after reset.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    # Stop if running
    if simulation_controller.is_running():
        await stop_simulation()

    # Reset state
    simulation_controller.reset()

    logger.info("Simulation reset")

    return get_status_response()


@router.post("/configure", status_code=status.HTTP_200_OK)
async def configure_simulation(config: SimulationConfigRequest):
    """
    Configure simulation parameters.

    Args:
        config: Simulation configuration.

    Returns:
        Simulation status after configuration.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    # Update configuration
    from src.agents.controller_agent import SimulationConfig

    new_config = SimulationConfig(
        max_rounds=config.max_rounds,
        event_probability=config.event_probability,
        checkpoint_interval=config.checkpoint_interval,
        checkpoint_dir=config.checkpoint_dir,
        log_level=config.log_level,
    )

    simulation_controller.config = new_config

    logger.info(f"Simulation configured: {config.dict()}")

    return get_status_response()


@router.get("/status", response_model=SimulationStatusResponse, status_code=status.HTTP_200_OK)
async def get_status() -> SimulationStatusResponse:
    """
    Get current simulation status.

    Returns:
        Current simulation status.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    return get_status_response()


def get_status_response() -> SimulationStatusResponse:
    """
    Build status response from controller.

    Returns:
        Simulation status response.
    """
    summary = simulation_controller.get_controller_summary()

    return SimulationStatusResponse(
        status=summary["status"],
        config=summary["config"],
        state=ControllerStateResponse(**summary["state"]),
        stats=ControllerStatsResponse(**summary["stats"]),
        agent_count=len(simulation_controller._agents),
        remaining_rounds=simulation_controller.get_remaining_rounds(),
    )
