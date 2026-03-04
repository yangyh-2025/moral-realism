"""
指标查询路由模块

本模块提供模拟指标查询的API端点：
- 当前指标
- 按回合范围查询历史指标
- 特定代理的指标
- 数据导出（CSV/JSON）

核心端点：
- GET /current: 获取当前模拟指标
- GET /trends: 获取指标趋势
- GET /agents/{agent_id}: 获取特定代理的指标历史
- GET /agents/{agent_id}/latest: 获取特定代理的最新指标
- GET /round/{round_id}: 获取特定回合的指标
- GET /export/csv: 导出CSV格式数据
- GET /export/json: 导出JSON格式数据
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Response, status

from api.models.schemas import MetricsResponse, SystemMetricsResponse


logger = logging.getLogger(__name__)
router = APIRouter()

# Global references
simulation_controller = None
data_storage = None


def set_controller(controller):
    """Set simulation controller reference."""
    global simulation_controller
    simulation_controller = controller


def set_storage(storage):
    """Set data storage reference."""
    global data_storage
    data_storage = storage


@router.get("/current", status_code=status.HTTP_200_OK)
async def get_current_metrics():
    """
    Get current simulation metrics.

    Returns:
        Current metrics for all agents and system.
    """
    if simulation_controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Simulation controller not initialized",
        )

    # Calculate metrics
    if simulation_controller._metrics_calculator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics calculator not configured",
        )

    try:
        metrics = simulation_controller._metrics_calculator.calculate_all_metrics(
            agents=simulation_controller._agents,
            state=simulation_controller.get_controller_summary(),
        )
        return metrics
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating metrics: {str(e)}",
        )


@router.get("/trends", status_code=status.HTTP_200_OK)
async def get_metrics_trends(
    start_round: int = 0,
    end_round: Optional[int] = None,
):
    """
    Get metric trends over multiple rounds.

    Args:
        start_round: Starting round number.
        end_round: Ending round number (optional).

    Returns:
        Metrics trends data.
    """
    if data_storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data storage not configured",
        )

    try:
        trends = data_storage.get_system_trends(start_round, end_round)
        return trends
    except Exception as e:
        logger.error(f"Error getting trends: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting trends: {str(e)}",
        )


@router.get("/agents/{agent_id}", status_code=status.HTTP_200_OK)
async def get_agent_metrics(
    agent_id: str,
    metric_type: Optional[str] = None,
):
    """
    Get metrics for a specific agent.

    Args:
        agent_id: Agent identifier.
        metric_type: Optional filter (capability, moral, success).

    Returns:
        Agent metrics history.
    """
    if data_storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data storage not configured",
        )

    if agent_id not in simulation_controller._agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {agent_id}",
        )

    try:
        history = data_storage.get_agent_history(agent_id, metric_type)
        return {
            "agent_id": agent_id,
            "metric_type": metric_type,
            "history": history,
            "count": len(history),
        }
    except Exception as e:
        logger.error(f"Error getting agent metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting agent metrics: {str(e)}",
        )


@router.get("/agents/{agent_id}/latest", status_code=status.HTTP_200_OK)
async def get_agent_latest_metrics(agent_id: str):
    """
    Get latest metrics for a specific agent.

    Args:
        agent_id: Agent identifier.

    Returns:
        Latest agent metrics.
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

    if simulation_controller._metrics_calculator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics calculator not configured",
        )

    try:
        agent = simulation_controller._agents[agent_id]
        metrics = simulation_controller._metrics_calculator._calculate_agent_metrics(
            agent,
            simulation_controller._round_executor._rule_environment
            if simulation_controller._round_executor else None,
            {},
            {},
        )
        return metrics.to_dict()
    except Exception as e:
        logger.error(f"Error getting latest metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting latest metrics: {str(e)}",
        )


@router.get("/round/{round_id}", status_code=status.HTTP_200_OK)
async def get_round_metrics(round_id: int):
    """
    Get metrics for a specific round.

    Args:
        round_id: Round number.

    Returns:
        Metrics for the specified round.
    """
    if data_storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data storage not configured",
        )

    try:
        metrics = data_storage.get_round_metrics(round_id)
        if metrics is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Round metrics not found: {round_id}",
            )
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting round metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting round metrics: {str(e)}",
        )


@router.get("/export/csv", status_code=status.HTTP_200_OK)
async def export_csv(
    data_type: str = "system_metrics",
    start_round: int = 0,
    end_round: Optional[int] = None,
):
    """
    Export metrics as CSV.

    Args:
        data_type: Type of data to export.
        start_round: Starting round.
        end_round: Ending round (optional).

    Returns:
        CSV file.
    """
    if data_storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data storage not configured",
        )

    try:
        # Create temporary file
        import tempfile
        filepath = data_storage.export_to_csv(data_type, tempfile.gettempdir(), start_round, end_round)

        if filepath is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to export {data_type}",
            )

        # Read and return file content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Clean up
        import os
        os.unlink(filepath)

        return Response(
            content=content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={data_type}.csv"
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting CSV: {str(e)}",
        )


@router.get("/export/json", status_code=status.HTTP_200_OK)
async def export_json(
    start_round: int = 0,
    end_round: Optional[int] = None,
):
    """
    Export metrics as JSON.

    Args:
        start_round: Starting round.
        end_round: Ending round (optional).

    Returns:
        JSON export.
    """
    if data_storage is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data storage not configured",
        )

    try:
        # Collect metrics for all rounds
        import os
        exports_dir = os.path.join(str(data_storage.base_dir), "outputs")

        if not os.path.exists(exports_dir):
            return {"rounds": [], "count": 0}

        metrics_list = []
        for filename in sorted(os.listdir(exports_dir)):
            if not filename.startswith("round_") or not filename.endswith(".json"):
                continue

            round_num = int(filename[6:-5])
            if round_num < start_round:
                continue
            if end_round is not None and round_num > end_round:
                continue

            filepath = os.path.join(exports_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                import json
                metrics_list.append(json.load(f))

        return {
            "rounds": metrics_list,
            "count": len(metrics_list),
            "start_round": start_round,
            "end_round": end_round,
        }
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting JSON: {str(e)}",
        )
