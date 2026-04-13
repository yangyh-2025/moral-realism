# Simulation Service
from typing import Optional
import asyncio
from sqlalchemy import select
from loguru import logger

from app.config.database import db_config
from app.models import SimulationProject


class SimulationService:
    """仿真流程控制服务"""

    def __init__(self):
        self.running_simulations = {}  # Track running simulations
        self.EVALUATION_INTERVAL = 10  # 评估间隔轮次

    async def start_simulation(self, project_id: int) -> dict:
        """
        启动仿真项目
        """
        # TODO: Implement actual simulation logic
        # This should initialize and run simulation engine

        return {
            "project_id": project_id,
            "status": "运行中",
            "message": "Simulation started"
        }

    async def step_simulation(self, project_id: int) -> dict:
        """
        单步执行一轮仿真
        """
        # TODO: Implement actual single step logic
        # Execute one round of simulation

        # 获取当前轮次
        current_round = await self._get_current_round(project_id)

        # 每10轮触发一次战略目标评估
        if current_round % self.EVALUATION_INTERVAL == 0 and current_round > 0:
            from app.services.goal_evaluation_service import get_goal_evaluation_service
            evaluation_service = get_goal_evaluation_service()

            try:
                await evaluation_service.evaluate_all_agents(project_id, current_round)
                logger.info(f"Goal evaluation completed at round {current_round}")
                eval_message = " (with goal evaluation)"
            except Exception as e:
                logger.error(f"Goal evaluation failed at round {current_round}: {e}")
                eval_message = " (evaluation failed)"
        else:
            eval_message = ""

        return {
            "project_id": project_id,
            "round": current_round,
            "status": "completed",
            "message": f"Step {current_round} executed{eval_message}"
        }

    async def _get_current_round(self, project_id: int) -> int:
        """获取项目当前轮次"""
        async for session in db_config.get_session():
            result = await session.execute(
                select(SimulationProject.current_round).where(
                    SimulationProject.project_id == project_id
                )
            )
            current_round = result.scalar_one_or_none()
            return current_round or 0

    async def pause_simulation(self, project_id: int) -> dict:
        """
        暂停仿真
        """
        # TODO: Implement actual pause logic
        if project_id in self.running_simulations:
            # Cancel the running task
            self.running_simulations[project_id].cancel()
            del self.running_simulations[project_id]


        return {
            "project_id": project_id,
            "status": "暂停",
            "message": "Simulation paused"
        }

    async def resume_simulation(self, project_id: int) -> dict:
        """
        继续仿真
        """
        # TODO: Implement actual resume logic
        # Continue from paused state

        return {
            "project_id": project_id,
            "status": "运行中",
            "message": "Simulation resumed"
        }

    async def stop_simulation(self, project_id: int) -> dict:
        """
        终止仿真
        """
        # TODO: Implement actual stop logic
        if project_id in self.running_simulations:
            self.running_simulations[project_id].cancel()
            del self.running_simulations[project_id]

        return {
            "project_id": project_id,
            "status": "已终止",
            "message": "Simulation stopped"
        }

    async def reset_simulation(self, project_id: int) -> dict:
        """
        重置仿真
        """
        # TODO: Implement actual reset logic
        # Clear all simulation data and restore to initial state

        return {
            "project_id": project_id,
            "status": "未启动",
            "message": "Simulation reset"
        }


# Singleton instance
simulation_service = SimulationService()
