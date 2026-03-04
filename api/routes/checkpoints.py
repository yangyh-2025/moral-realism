"""
检查点管理路由模块

本模块提供模拟检查点管理的API端点：
- 列出可用检查点
- 保存检查点
- 加载检查点
- 删除检查点

核心端点：
- GET /: 列出所有检查点
- GET /{checkpoint_id}: 获取特定检查点信息
- POST /save: 保存当前状态为检查点
- POST /load/{checkpoint_id}: 加载指定检查点
- DELETE /{checkpoint_id}: 删除指定检查点
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from api.models.schemas import CheckpointListResponse, CheckpointResponse


logger = logging.getLogger(__name__)
router = APIRouter()

# Global reference to simulation controller
simulation_controller = None


def set_controller(controller):
    """Set simulation controller reference."""
    global simulation_controller
    simulation_controller = controller


@router.get("/", response_model=CheckpointListResponse, status_code=status.HTTP_200_OK)
async def list_checkpoints() -> CheckpointListResponse:
    """
    List all available checkpoints.

    Returns:
        List of checkpoints.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    if simulation_controller._data_storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data storage not configured",
        )

    try:
        checkpoint_ids = simulation_controller._data_storage.list_checkpoints()

        checkpoints = []
        for checkpoint_id in checkpoint_ids:
            # Load checkpoint to get metadata
            checkpoint_data = simulation_controller._data_storage.load_checkpoint(checkpoint_id)
            if checkpoint_data:
                checkpoints.append(CheckpointResponse(
                    checkpoint_id=checkpoint_id,
                    timestamp=checkpoint_data.get("timestamp", ""),
                    round=checkpoint_data.get("state", {}).get("round_number"),
                    agent_count=len(checkpoint_data.get("state", {}).get("agents", {})),
                ))

        return CheckpointListResponse(
            checkpoints=checkpoints,
            count=len(checkpoints),
        )
    except Exception as e:
        logger.error(f"Error listing checkpoints: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing checkpoints: {str(e)}",
        )


@router.get("/{checkpoint_id}", response_model=CheckpointResponse, status_code=status.HTTP_200_OK)
async def get_checkpoint(checkpoint_id: str) -> CheckpointResponse:
    """
    Get information about a specific checkpoint.

    Args:
        checkpoint_id: Checkpoint identifier.

    Returns:
        Checkpoint information.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    if simulation_controller._data_storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data storage not configured",
        )

    try:
        checkpoint_data = simulation_controller._data_storage.load_checkpoint(checkpoint_id)
        if checkpoint_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Checkpoint not found: {checkpoint_id}",
            )

        return CheckpointResponse(
            checkpoint_id=checkpoint_id,
            timestamp=checkpoint_data.get("timestamp", ""),
            round=checkpoint_data.get("state", {}).get("round_number"),
            agent_count=len(checkpoint_data.get("state", {}).get("agents", {})),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting checkpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting checkpoint: {str(e)}",
        )


@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_checkpoint(checkpoint_id: Optional[str] = None):
    """
    Save current simulation state as checkpoint.

    Args:
        checkpoint_id: Optional checkpoint ID (auto-generated if not provided).

    Returns:
        Checkpoint information.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    try:
        # Capture snapshot using state manager
        if simulation_controller._state_manager is None:
            # Create simple state without state manager
            state_dict = {
                "round_number": simulation_controller.state.current_round,
                "agents": {},
            }
        else:
            from src.workflow.state_manager import SimulationSnapshot
            snapshot = simulation_controller._state_manager.capture_state(
                round_number=simulation_controller.state.current_round,
                additional_context={},
            )
            state_dict = snapshot.to_dict()

        # Save checkpoint
        saved_path = simulation_controller.save_checkpoint(checkpoint_id)

        if saved_path is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save checkpoint",
            )

        # Extract checkpoint ID from path
        import os
        filename = os.path.basename(saved_path)
        actual_checkpoint_id = filename.replace("checkpoint_", "").replace(".json", "")

        logger.info(f"Checkpoint saved: {actual_checkpoint_id}")

        return CheckpointResponse(
            checkpoint_id=actual_checkpoint_id,
            timestamp=saved_path,
            round=state_dict.get("round_number"),
            agent_count=len(state_dict.get("agents", {})),
        )
    except Exception as e:
        logger.error(f"Error saving checkpoint: {e}", exc_info=True)
        raise HTTPException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving checkpoint: {str(e)}",
        )


@router.post("/load/{checkpoint_id}", status_code=status.HTTP_200_OK)
async def load_checkpoint(checkpoint_id: str):
    """
    Load simulation state from checkpoint.

    Args:
        checkpoint_id: Checkpoint identifier.

    Returns:
        Loading confirmation.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    try:
        success = simulation_controller.load_checkpoint(checkpoint_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to load checkpoint: {checkpoint_id}",
            )

        logger.info(f"Checkpoint loaded: {checkpoint_id}")

        return {
            "message": f"Checkpoint loaded: {checkpoint_id}",
            "checkpoint_id": checkpoint_id,
            "status": simulation_controller.get_status().value,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading checkpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading checkpoint: {str(e)}",
        )


@router.delete("/{checkpoint_id}", status_code=status.HTTP_200_OK)
async def delete_checkpoint(checkpoint_id: str):
    """
    Delete a checkpoint.

    Args:
        checkpoint_id: Checkpoint identifier.

    Returns:
        Deletion confirmation.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    if simulation_controller._data_storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data storage not configured",
        )

    try:
        import os
        filepath = os.path.join(
            str(simulation_controller._data_storage.base_dir),
            "checkpoints",
            f"checkpoint_{checkpoint_id}.json"
        )

        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Checkpoint not found: {checkpoint_id}",
            )

        os.unlink(filepath)

        logger.info(f"Checkpoint deleted: {checkpoint_id}")

        return {"message": f"Checkpoint deleted: {checkpoint_id}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting checkpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting checkpoint: {str(e)}",
        )
